"""Analysis + bookkeeping tools: jwt, skills, notes, findings, external, finish."""
from __future__ import annotations

import base64
import hashlib
import hmac as _hmac
import json
import os
import re
import shutil
import subprocess
import urllib.parse
from pathlib import Path

from ..scope import ScopeError
from .registry import Context

# ---------------------------------------------------------------- jwt

_COMMON_SECRETS = [
    "secret", "secret123", "password", "changeme", "key", "private", "admin",
    "test", "dev", "12345", "jwtsecret", "your-256-bit-secret", "supersecret",
    "HS256", "hmac", "default", "letmein", "qwerty", "argus",
]


def _b64url(part: str) -> bytes:
    pad = "=" * (-len(part) % 4)
    return base64.urlsafe_b64decode(part + pad)


def jwt_decode(ctx: Context, token: str) -> dict:
    token = token.strip().strip('"\'')
    parts = token.split(".")
    if len(parts) not in (2, 3):
        return {"error": "not a JWT (expected 2 or 3 segments)"}
    try:
        header = json.loads(_b64url(parts[0]))
        payload = json.loads(_b64url(parts[1]))
    except (ValueError, json.JSONDecodeError) as exc:
        return {"error": f"decode failed: {exc}"}
    out: dict = {"header": header, "payload": payload}
    alg = (header.get("alg") or "").lower()
    issues = []
    if alg == "none":
        issues.append("alg=none token presented - try dropping the signature")
    if alg.startswith("hs") and len(parts) == 3:
        signing_input = f"{parts[0]}.{parts[1]}".encode()
        sig = _b64url(parts[2])
        algo = {"hs256": hashlib.sha256, "hs384": hashlib.sha384,
                "hs512": hashlib.sha512}[alg]
        for secret in _COMMON_SECRETS:
            cand = _hmac.new(secret.encode(), signing_input, algo).digest()
            if _hmac.compare_digest(cand, sig):
                issues.append(f"weak HMAC secret recovered offline: {secret!r}")
                out["recovered_secret"] = secret
                break
    if alg.startswith("rs") or alg.startswith("es"):
        issues.append(f"{alg}: check for alg-confusion (RS256->HS256 with public key) and jku/kid injection")
    exp = payload.get("exp")
    if exp:
        import time
        out["expired"] = exp < time.time()
    out["issues"] = issues or ["no obvious weakness; need the signing key or a confused verifier"]
    return out


# ---------------------------------------------------------------- skills

def load_skill(ctx: Context, name: str) -> dict:
    skills_dir = Path(ctx.skills_dir)
    if name.strip().lower() in ("index", "list", ""):
        index = skills_dir / "INDEX.md"
        listing = sorted(p.stem for p in skills_dir.glob("*.md") if p.name != "INDEX.md")
        return {"available": listing,
                "index": index.read_text(encoding="utf-8") if index.exists() else ""}
    safe = re.sub(r"[^a-z0-9_-]", "", name.lower())
    path = skills_dir / f"{safe}.md"
    if not path.exists():
        return {"error": f"no skill named {name!r}; call load_skill('index')"}
    return {"skill": safe, "content": path.read_text(encoding="utf-8")}


# ---------------------------------------------------------------- notes

def note(ctx: Context, text: str) -> dict:
    ctx.session.note(text)
    return {"ok": True}


def read_notes(ctx: Context) -> dict:
    return {"notes": ctx.session.notes_path.read_text(encoding="utf-8")}


# ---------------------------------------------------------------- findings

def record_finding(ctx: Context, title: str, severity: str, category: str,
                   url: str, evidence_ids: list[str], evidence_excerpt: str,
                   description: str, remediation: str) -> dict:
    finding = ctx.session.add_finding(
        title=title, severity=severity, category=category, url=url,
        evidence_ids=list(evidence_ids or []),
        evidence_excerpt=evidence_excerpt, description=description,
        remediation=remediation, agent=ctx.agent_name,
    )
    return {"recorded": finding["id"], "title": finding["title"],
            "severity": finding["severity"]}


# ---------------------------------------------------------------- external

_ALLOWED_TOOLS = {"sqlmap", "nuclei", "nmap", "ffuf", "curl"}
_URL_RE = re.compile(r"https?://[^\s'\"]+")
_HOST_RE = re.compile(
    r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}|"
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d{1,2})?")


def run_external(ctx: Context, tool: str, args: str, timeout_s: int = 120) -> dict:
    if not ctx.cfg.external_tools:
        return {"error": "external tools disabled (--no-external)"}
    tool = tool.strip().lower()
    if tool not in _ALLOWED_TOOLS:
        return {"error": f"tool {tool!r} not allowed; allowed: {sorted(_ALLOWED_TOOLS)}"}
    binary = shutil.which(tool)
    if not binary:
        return {"error": f"{tool} is not installed on this host"}
    for u in _URL_RE.findall(args):
        ctx.scope.check(u)  # raises ScopeError -> returned as error
    # bare hostnames/IPs as arguments (e.g. `nmap evil.com`) must also be
    # in scope; flags and existing filenames are skipped
    for tok in _split_args(args):
        if tok.startswith("-") or Path(tok).exists() or os.sep in tok:
            continue
        host_part = tok.split(":")[0]
        if re.search(r"\.(?:txt|xml|json|html?|list|lst|md|csv|out|log|yaml|yml|py|sh|gz|zip)$",
                     host_part, re.I):
            continue  # file-like, not a hostname
        if _HOST_RE.fullmatch(host_part):
            ctx.scope.check("http://" + host_part)
    timeout_s = max(5, min(int(timeout_s or 120), 600))
    cmd = [binary] + _split_args(args)
    rid = ctx.session.record_event("external_cmd", {"cmd": cmd})
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              timeout=timeout_s, errors="replace")
        output = (proc.stdout or "") + ("\n[stderr]\n" + proc.stderr if proc.stderr else "")
        ctx.session.record_event("external_result", {
            "cmd_id": rid, "returncode": proc.returncode,
            "output": output[:50_000]})
        return {"cmd_id": rid, "returncode": proc.returncode,
                "output": output[-20_000:],
                "note": "scanner output is a lead; verify with http_request before record_finding"}
    except subprocess.TimeoutExpired:
        ctx.session.record_event("external_result", {"cmd_id": rid, "timeout": timeout_s})
        return {"cmd_id": rid, "error": f"timed out after {timeout_s}s"}


def _split_args(args: str) -> list[str]:
    import shlex
    try:
        return shlex.split(args, posix=False) if _is_windows() else shlex.split(args)
    except ValueError:
        return args.split()


def _is_windows() -> bool:
    import os
    return os.name == "nt"


# ---------------------------------------------------------------- finish

def finish(ctx: Context, summary: str) -> dict:
    ctx.finished = True
    ctx.finish_summary = summary
    ctx.session.note(f"## Agent summary\n\n{summary}")
    return {"finished": True, "stats": ctx.session.stats()}
