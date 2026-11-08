"""Team-mode tools: leads pipeline, blackboard, spawn requests,
wordlist-driven fuzzing, and the resources/exploits manifest runner."""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.parse
from pathlib import Path

from ..team.leads import Lead
from .registry import Context

# Bundled defaults ship inside the package (wheels), a <cwd>/resources/
# tree lets an operator extend wordlists/exploits without touching the
# install — the cwd copy wins on name collisions.
RESOURCES = Path(__file__).resolve().parents[1] / "resources"
RESOURCES_USER = Path.cwd() / "resources"
WORDLISTS = RESOURCES / "wordlists"
WORDLISTS_USER = RESOURCES_USER / "wordlists"
EXPLOITS = RESOURCES / "exploits"
EXPLOITS_USER = RESOURCES_USER / "exploits"


def _board(ctx: Context):
    if ctx.board is None:
        raise RuntimeError("team tools require a board (single-agent mode has none)")
    return ctx.board


# ------------------------------------------------------------- pipeline

def emit_lead(ctx: Context, kind: str, url: str, params: list | None = None,
              method: str = "GET", tech: str = "", note: str = "",
              source: str = "", priority: int = 5) -> dict:
    board = _board(ctx)
    kind = (kind or "endpoint").lower()
    if kind not in ("endpoint", "param", "credential", "note"):
        return {"error": f"kind must be endpoint|param|credential|note, got {kind!r}"}
    if kind in ("endpoint", "param"):
        try:
            ctx.scope.check(url)
        except Exception as exc:
            return {"error": f"lead url rejected by scope guard: {exc}"}
    lead = Lead(kind=kind, url=url.strip(),
                params=tuple(sorted(params or [])),
                method=(method or "GET").upper(), tech=tech, note=note,
                source=source or ctx.agent_name,
                priority=max(0, min(int(priority or 5), 9)))
    if not board.leads.push(lead):
        return {"queued": False, "reason": "duplicate of an existing lead"}
    return {"queued": True, "pending": board.leads.pending}


def pull_leads(ctx: Context, max_n: int = 5, wait_s: int = 20) -> dict:
    board = _board(ctx)
    leads, closed = board.leads.pull(max_n=max(1, min(int(max_n or 5), 10)),
                                   wait_s=max(1, min(int(wait_s or 20), 60)))
    if closed and not leads:
        return {"leads": [], "closed": True,
                "hint": "queue closed and drained - call finish()"}
    out = {"leads": [l.to_dict() for l in leads], "closed": False,
           "pending": board.leads.pending}
    if not leads:
        out["hint"] = "no leads yet; recon is still running - pull again"
    return out


# ------------------------------------------------------------- board

def read_board(ctx: Context) -> dict:
    return _board(ctx).snapshot(consume_requests=(ctx.role == "lead"))


def post_board_note(ctx: Context, text: str) -> dict:
    _board(ctx).post_note(ctx.agent_name, text)
    return {"ok": True}


def request_worker(ctx: Context, role: str, task: str, reason: str = "") -> dict:
    board = _board(ctx)
    role = (role or "").lower()
    if role not in ("recon", "exploit", "report"):
        return {"error": f"role must be recon|exploit|report, got {role!r}"}
    if not task.strip():
        return {"error": "task is required"}
    board.request_worker(ctx.agent_name, role, task.strip(), reason.strip())
    return {"requested": True,
            "note": "the lead sees this on read_board and decides whether to spawn"}


# ------------------------------------------------------------- lead only

def spawn_worker(ctx: Context, role: str, task: str) -> dict:
    board = _board(ctx)
    return board.spawn((role or "").lower(), (task or "").strip())


def list_workers(ctx: Context) -> dict:
    return {"agents": _board(ctx).agents()}


def read_findings(ctx: Context) -> dict:
    """Slim view for dedup decisions - workers only need class+endpoint+id
    to skip already-proven work; full bodies live in findings.json."""
    slim = [{k: f.get(k) for k in
             ("id", "title", "severity", "category", "url")}
            for f in ctx.session.findings]
    return {"findings": slim, "count": len(slim)}


def finish_engagement(ctx: Context, summary: str) -> dict:
    board = _board(ctx)
    board.leads.close()
    board.engagement_done.set()
    ctx.finished = True
    ctx.finish_summary = summary
    ctx.session.note(f"## Lead summary\n\n{summary}")
    return {"finished": True, "queue_closed": True,
            "stats": ctx.session.stats()}


# ------------------------------------------------------------- wordlists

def _load_wordlist(name: str) -> tuple[list[str], str | None]:
    safe = re.sub(r"[^a-z0-9_-]", "", (name or "").lower())
    if not safe:
        return [], f"bad wordlist name {name!r}; use a file stem from resources/wordlists/"
    path = WORDLISTS_USER / f"{safe}.txt"
    if not path.exists():
        path = WORDLISTS / f"{safe}.txt"
    if not path.exists():
        avail = sorted({p.stem for d in (WORDLISTS, WORDLISTS_USER)
                        if d.exists() for p in d.glob("*.txt")})
        return [], f"no wordlist {safe!r}; available: {avail}"
    words = [w.strip() for w in path.read_text(encoding="utf-8").splitlines()
             if w.strip() and not w.startswith("#")]
    return words, None


def wordlist_fuzz(ctx: Context, base_url: str, wordlist: str = "dirs-small",
                  mode: str = "path", param: str = "", max_words: int = 80,
                  statuses: str = "", method: str = "GET",
                  data: str | None = None) -> dict:
    """Probe one wordlist-driven surface. mode=path appends each word to
    base_url; mode=param sets ?param=word (GET) or injects the word into
    a POST body template (method=POST, data='u=x&p={{param}}'). Every
    request still passes the scope guard, rate limiter and budget."""
    from .probes import _inject_body
    ctx.scope.check(base_url)  # fail fast before burning the budget
    words, err = _load_wordlist(wordlist)
    if err:
        return {"error": err}
    max_words = max(1, min(int(max_words or 80), 400))
    words = words[:max_words]
    keep = None
    if statuses.strip():
        keep = {int(s) for s in re.split(r"[^0-9]+", statuses) if s}
    sep = "&" if "?" in base_url else "?"
    method = (method or "GET").upper()
    post = method != "GET" and data is not None
    headers = None
    if post:
        headers = ({"Content-Type": "application/json"}
                   if data.strip().startswith("{")
                   else {"Content-Type": "application/x-www-form-urlencoded"})
    hits, tested = [], 0
    for w in words:
        body = None
        if mode == "param":
            if not param:
                return {"error": "mode=param requires a param name"}
            if post:
                url = base_url
                body = (data.replace("{{param}}", w)
                        if "{{param}}" in data
                        else _inject_body(data, param, w))
            else:
                url = base_url + sep + urllib.parse.urlencode({param: w})
        else:
            url = base_url.rstrip("/") + "/" + w.lstrip("/")
        r = ctx.client.send(method if post else "GET", url,
                            headers=headers, body=body,
                            tool="wordlist_fuzz",
                            note=f"wl:{wordlist}:{w}")
        tested += 1
        st = r.get("status", 0)
        interesting = (st in keep) if keep else (st not in (0, 404))
        if interesting:
            hits.append({"word": w, "status": st, "rid": r["request_id"],
                         "bytes": len(r.get("body") or "")})
    return {"tested": tested, "interesting": hits,
            "note": "a hit is a lead: emit_lead() the promising ones"}


# ------------------------------------------------------------- exploits

def _exploit_dirs() -> list[Path]:
    """All manifest dirs, user tree first (it shadows bundled ids)."""
    seen, out = set(), []
    for root in (EXPLOITS_USER, EXPLOITS):
        if not root.exists():
            continue
        for d in sorted(root.iterdir()):
            if d.is_dir() and (d / "manifest.json").exists() \
                    and d.name not in seen:
                seen.add(d.name)
                out.append(d)
    return out


def _load_manifest(exploit_id: str) -> tuple[dict | None, Path | None, str | None]:
    safe = re.sub(r"[^a-z0-9_-]", "", (exploit_id or "").lower())
    for root in (EXPLOITS_USER, EXPLOITS):
        d = root / safe
        mpath = d / "manifest.json"
        if mpath.exists():
            try:
                return json.loads(mpath.read_text(encoding="utf-8")), d, None
            except (ValueError, OSError) as exc:
                return None, None, f"bad manifest for {safe!r}: {exc}"
    avail = sorted(d.name for d in _exploit_dirs())
    return None, None, f"no exploit {safe!r}; available: {avail}"


def list_exploits(ctx: Context) -> dict:
    out = []
    for d in _exploit_dirs():
        try:
            meta = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
            out.append({"id": d.name, "title": meta.get("title", ""),
                        "affects": meta.get("affects", []),
                        "cve": meta.get("cve")})
        except ValueError:
            out.append({"id": d.name, "error": "bad manifest"})
    return {"exploits": out}


def run_exploit(ctx: Context, exploit_id: str, target: str,
                args: str = "", timeout_s: int = 60) -> dict:
    """Run a manifest-declared exploit script. The target URL is scope-checked
    and substituted into the command as {target}; the run is timeout-bounded
    and its output is recorded. proof_marker match = verified exploit."""
    manifest, edir, err = _load_manifest(exploit_id)
    if err:
        return {"error": err}
    try:
        ctx.scope.check(target)  # the script may only see in-scope targets
    except Exception as exc:
        return {"error": f"target rejected by scope guard: {exc}"}
    # {args} is free text smuggled into the command line - it must not
    # carry a foreign URL/host past the guard either (URLs, bare hosts,
    # IPv6 literals - same scan as run_external)
    from .analysis import _args_scope_check
    try:
        _args_scope_check(ctx, args or "")
    except Exception as exc:
        return {"error": f"args rejected by scope guard: {exc}"}
    cmd_tpl = manifest.get("command")
    if not cmd_tpl:
        return {"error": "manifest has no command"}
    cmd = [part.replace("{target}", target).replace("{args}", args or "")
           for part in cmd_tpl]
    if Path(cmd[0]).is_absolute():
        script = Path(cmd[0])
    else:
        script = (edir / cmd[0]).resolve()
        # relative entry points stay inside the exploit's own directory
        if not script.is_relative_to(edir.resolve()):
            return {"error": "manifest command escapes the exploit dir"}
    cmd[0] = str(script)
    if cmd[0].endswith(".py"):
        import sys
        cmd = [sys.executable] + cmd
    timeout_s = max(5, min(int(timeout_s or manifest.get("timeout_s", 60)), 300))
    try:
        # exploit PoCs are the least-trusted local code (often downloaded)
        # - scrub credentials from the environment they inherit
        from ..mcp import MCPClient
        env = {k: v for k, v in os.environ.items()
               if not any(s in k.upper() for s in MCPClient._SECRET_RE)}
        from ._subproc import run_capped
        marker = manifest.get("proof_marker") or ""
        rc, head, tail, proof = run_capped(
            cmd, timeout_s, cwd=str(edir), env=env,
            needle=marker or None)
        proof = proof and bool(marker)
    except subprocess.TimeoutExpired:
        rid = ctx.session.record_event("exploit_run", {
            "exploit": exploit_id, "cmd": cmd, "timeout": timeout_s},
            agent=ctx.agent_name)
        return {"run_id": rid, "error": f"timed out after {timeout_s}s"}
    rid = ctx.session.record_event("exploit_run", {
        "exploit": exploit_id, "cmd": cmd, "returncode": rc,
        "proof": proof, "output": head[:50_000]}, agent=ctx.agent_name)
    return {"run_id": rid, "returncode": rc, "proof": proof,
            "output": tail[-15_000:],
            "note": "proof=True verifies the exploit; cite run_id as evidence "
                    "for record_finding" if proof else
                    "no proof_marker match - treat as a lead, not a finding"}
