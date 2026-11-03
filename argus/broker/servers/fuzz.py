"""fuzz — content and parameter discovery.

The only thing this server adds over running ffuf by hand is discipline: a
calibrated filter so a soft-404 page does not come back as two thousand hits, a
cap on wall time so a wordlist cannot eat the engagement, and every result
written into the ledger as surface rather than into a scrollback buffer.
"""
from __future__ import annotations

import json
import os
import urllib.parse

from ... import config
from ...ledger.state import RECON
from .. import exec as ex
from ..mcp import Server, ToolContext, ToolError

SERVER = Server("fuzz", "content and parameter discovery")

WORDLIST_CANDIDATES = (
    "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt",
    "/usr/share/seclists/Discovery/Web-Content/common.txt",
    "/usr/share/wordlists/dirb/common.txt",
    "/usr/share/wordlists/dirb/big.txt",
    "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt",
)
PARAM_WORDLIST_CANDIDATES = (
    "/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt",
    "/usr/share/wordlists/wfuzz/general/common.txt",
    "/usr/share/wordlists/dirb/common.txt",
)


def _pick_wordlist(explicit: str, candidates: tuple[str, ...]) -> str:
    if explicit:
        if not os.path.isfile(explicit):
            raise ToolError(f"wordlist not found: {explicit}")
        return explicit
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    raise ToolError("no wordlist available. Install seclists (apt install seclists) or pass "
                    "wordlist=<path>")


def _ffuf(argv: list[str], context: ToolContext, timeout: int) -> tuple[list[dict], object]:
    result = ex.run(argv, timeout=timeout, log_path=context.command_log)
    hits = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "status" in record and "url" in record:
            hits.append({"url": record.get("url"), "status": record.get("status"),
                         "length": record.get("length"), "words": record.get("words"),
                         "input": (record.get("input") or {}).get("FUZZ")
                                  or (record.get("input") or {}).get("W1"),
                         "redirect": record.get("redirectlocation") or ""})
    return hits, result


@SERVER.tool(
    "fuzz.content",
    "Discover paths the application does not link, with ffuf. Auto-calibration is on by default, "
    "which is what keeps a soft-404 from returning the whole wordlist, and a wall-clock cap is "
    "always applied. Every hit is recorded as surface.",
    {"properties": {
        "target": {"type": "string", "description": "base URL; FUZZ is appended as a path segment"},
        "wordlist": {"type": "string", "description": "path; a sensible installed list by default"},
        "extensions": {"type": "string", "description": "comma separated, e.g. .php,.bak,.json"},
        "match_codes": {"type": "string", "description": "ffuf -mc value; default 200,204,301,302,307,401,403,405,500"},
        "threads": {"type": "integer", "description": "default 25"},
        "max_seconds": {"type": "integer", "description": "wall-clock cap, default 180"},
        "headers": {"type": "object"}, "cookies": {"type": "string"},
    }, "required": ["target"]},
    tier=config.TIER_ACTIVE, vuln_class=RECON, step="content-discovery", requires=("ffuf",),
)
def content(context: ToolContext, target: str, wordlist: str = "", extensions: str = "",
            match_codes: str = "200,204,301,302,307,401,403,405,500", threads: int = 25,
            max_seconds: int = 180, headers: dict | None = None, cookies: str = "") -> dict:
    base = target.rstrip("/")
    if "://" not in base:
        base = "http://" + base
    chosen = _pick_wordlist(wordlist, WORDLIST_CANDIDATES)
    argv = ["ffuf", "-u", f"{base}/FUZZ", "-w", f"{chosen}:FUZZ", "-mc", match_codes,
            "-ac", "-t", str(max(1, min(int(threads), 60))), "-s", "-json",
            "-maxtime", str(max(10, min(int(max_seconds), 900))), "-timeout", "10"]
    if extensions:
        argv += ["-e", extensions]
    for name, value in (headers or {}).items():
        argv += ["-H", f"{name}: {value}"]
    if cookies:
        argv += ["-H", f"Cookie: {cookies}"]
    hits, result = _ffuf(argv, context, timeout=max_seconds + 60)
    for hit in hits:
        path = urllib.parse.urlsplit(hit["url"]).path or "/"
        context.emit_surface(target, "endpoint", path,
                             detail={"status": hit["status"], "length": hit["length"],
                                     "redirect": hit["redirect"]})
    listing = [f"{h['status']} {h['length']:>8}  {h['url']}" for h in hits[:200]]
    return {
        "summary": f"{len(hits)} path(s) on {base} from {os.path.basename(chosen)}",
        "result": "signal" if hits else "no-signal",
        "argv": argv, "exit_code": result.exit_code, "duration_ms": result.duration_ms,
        "data": {"wordlist": chosen, "hits": hits[:200]},
        "output": "\n".join(listing)[:6000] or result.text(2000),
        "evidence": {"kind": "probe", "target": target, "tool": "ffuf", "command": argv,
                     "extracted": {"hit_count": len(hits),
                                   "paths": [h["url"] for h in hits[:80]]}},
        "next": "a 403 is surface too: it says the path exists and something guards it",
    }


@SERVER.tool(
    "fuzz.params",
    "Find parameters an endpoint accepts but does not advertise, by fuzzing parameter names and "
    "keeping only the ones that change the response. Use it when recon.params found an endpoint "
    "with no visible inputs.",
    {"properties": {
        "target": {"type": "string", "description": "endpoint URL"},
        "wordlist": {"type": "string"},
        "method": {"type": "string", "enum": ["GET", "POST"]},
        "value": {"type": "string", "description": "the value given to each candidate name"},
        "filter_size": {"type": "string", "description": "ffuf -fs value; default is auto-calibrated"},
        "threads": {"type": "integer"}, "max_seconds": {"type": "integer"},
    }, "required": ["target"]},
    tier=config.TIER_ACTIVE, vuln_class=RECON, step="parameter-discovery", requires=("ffuf",),
)
def params(context: ToolContext, target: str, wordlist: str = "", method: str = "GET",
           value: str = "argusprobe", filter_size: str = "", threads: int = 25,
           max_seconds: int = 180) -> dict:
    chosen = _pick_wordlist(wordlist, PARAM_WORDLIST_CANDIDATES)
    separator = "&" if "?" in target else "?"
    if method == "GET":
        url = f"{target}{separator}FUZZ={value}"
        argv = ["ffuf", "-u", url, "-w", f"{chosen}:FUZZ"]
    else:
        argv = ["ffuf", "-u", target, "-X", "POST", "-d", f"FUZZ={value}",
                "-H", "Content-Type: application/x-www-form-urlencoded", "-w", f"{chosen}:FUZZ"]
    argv += ["-ac", "-mc", "all", "-s", "-json", "-t", str(max(1, min(int(threads), 60))),
             "-maxtime", str(max(10, min(int(max_seconds), 900))), "-timeout", "10"]
    if filter_size:
        argv += ["-fs", filter_size]
    hits, result = _ffuf(argv, context, timeout=max_seconds + 60)
    for hit in hits:
        if hit.get("input"):
            context.emit_surface(target, "param", hit["input"],
                                 detail={"source": "fuzz.params", "status": hit["status"]})
    return {
        "summary": f"{len(hits)} candidate parameter name(s) changed the response on {target}",
        "result": "signal" if hits else "no-signal",
        "argv": argv, "exit_code": result.exit_code, "duration_ms": result.duration_ms,
        "data": {"wordlist": chosen, "hits": hits[:120]},
        "output": "\n".join(f"{h['input']} -> {h['status']} {h['length']}B" for h in hits[:120]),
        "evidence": {"kind": "probe", "target": target, "tool": "ffuf", "command": argv,
                     "extracted": {"parameters": [h.get("input") for h in hits[:60]]}},
        "next": "confirm each candidate with http.differential before opening a hypothesis on it",
    }
