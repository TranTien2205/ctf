"""Team-mode tools: leads pipeline, blackboard, spawn requests,
wordlist-driven fuzzing, and the resources/exploits manifest runner."""
from __future__ import annotations

import json
import os
import re
import subprocess
import urllib.parse
from pathlib import Path

from ..team.leads import Lead
from .registry import Context, _ival

# Bundled defaults ship inside the package (wheels). A <cwd>/resources/
# tree lets an operator extend wordlists without touching the install —
# the cwd copy wins on name collisions. Exploits are different: their
# manifests name commands to run, so a cwd tree only loads with
# ARGUS_EXPLOITS_CWD=1 - otherwise running argus inside an untrusted
# directory (e.g. extracted target source) would let a planted manifest
# execute arbitrary commands through the model.
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

_LEAD_REFUSALS = {
    "closed": "the lead pipeline is closed - the engagement is wrapping up, "
              "so stop emitting leads; they will not be pulled",
    "duplicate": "duplicate of an existing lead - go find different surface",
    "capacity": "the lead queue is full (10000 unique leads) - nothing is "
                "wrong with this lead and the surface is NOT covered; the "
                "queue stopped accepting",
}


def emit_lead(ctx: Context, kind: str, url: str, params: list | None = None,
              method: str = "GET", tech: str = "", note: str = "",
              source: str = "", priority: int = 5) -> dict:
    board = _board(ctx)
    kind = str(kind or "endpoint").lower()
    if kind not in ("endpoint", "param", "credential", "note"):
        return {"error": f"kind must be endpoint|param|credential|note, got {kind!r}"}
    if kind in ("endpoint", "param"):
        try:
            ctx.scope.check(url)
        except Exception as exc:
            return {"error": f"lead url rejected by scope guard: {exc}"}
    url = str(url or "")
    if isinstance(params, (list, tuple)):
        params = [str(p) for p in params][:50]
    else:
        params = []
    try:
        prio = int(priority or 5)
    except (TypeError, ValueError):
        prio = 5
    lead = Lead(kind=kind, url=url.strip()[:2000],
                params=tuple(sorted(params)),
                method=str(method or "GET").upper(),
                tech=str(tech or "")[:500], note=str(note or "")[:2000],
                source=str(source or ctx.agent_name),
                priority=max(0, min(prio, 9)))
    refusal = board.leads.offer(lead)
    if refusal:
        # the reason decides what the worker should do next, so report the
        # one that actually applied instead of calling all three "duplicate"
        return {"queued": False, "reason": _LEAD_REFUSALS[refusal],
                "refusal": refusal}
    return {"queued": True, "pending": board.leads.pending}


def pull_leads(ctx: Context, max_n: int = 5, wait_s: int = 20) -> dict:
    board = _board(ctx)
    leads, closed = board.leads.pull(max_n=_ival(max_n, 5, 1, 10),
                                   wait_s=_ival(wait_s, 20, 1, 60))
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
    _board(ctx).post_note(ctx.agent_name, str(text))
    return {"ok": True}


def request_worker(ctx: Context, role: str, task: str, reason: str = "") -> dict:
    board = _board(ctx)
    role = str(role or "").lower()
    if role not in ("recon", "exploit", "report"):
        return {"error": f"role must be recon|exploit|report, got {role!r}"}
    task = task if isinstance(task, str) else ""
    if not task.strip():
        return {"error": "task is required"}
    reason = reason if isinstance(reason, str) else ""
    board.request_worker(ctx.agent_name, role, task.strip(), reason.strip())
    return {"requested": True,
            "note": "the lead sees this on read_board and decides whether to spawn"}


# ------------------------------------------------------------- lead only

def spawn_worker(ctx: Context, role: str, task: str) -> dict:
    board = _board(ctx)
    return board.spawn(str(role or "").lower(),
                       str(task or "").strip())


def list_workers(ctx: Context) -> dict:
    return {"agents": _board(ctx).agents()}


def read_findings(ctx: Context) -> dict:
    """Slim view for dedup decisions - workers only need class+endpoint+id
    to skip already-proven work; full bodies live in findings.json."""
    rows = ctx.session.findings
    slim = [{k: f.get(k) for k in
             ("id", "title", "severity", "category", "url")}
            for f in rows[-200:] if isinstance(f, dict)]
    return {"findings": slim, "count": len(rows),
            "returned": len(slim),
            "note": "last 200 shown; dedup by category+url anyway"}


def finish_engagement(ctx: Context, summary: str) -> dict:
    board = _board(ctx)
    board.leads.close()
    board.engagement_done.set()
    ctx.finished = True
    ctx.finish_summary = summary if isinstance(summary, str) else str(summary)
    ctx.session.note(f"## Lead summary\n\n{ctx.finish_summary}")
    return {"finished": True, "queue_closed": True,
            "stats": ctx.session.stats()}


# ------------------------------------------------------------- wordlists

def _load_wordlist(name: str, limit: int = 50_000) -> tuple[list[str], str | None]:
    safe = re.sub(r"[^a-z0-9_-]", "", str(name or "").lower())
    if not safe:
        return [], f"bad wordlist name {name!r}; use a file stem from resources/wordlists/"
    path = WORDLISTS_USER / f"{safe}.txt"
    if not path.exists():
        path = WORDLISTS / f"{safe}.txt"
    if not path.exists():
        avail = sorted({p.stem for d in (WORDLISTS, WORDLISTS_USER)
                        if d.exists() for p in d.glob("*.txt")})
        return [], f"no wordlist {safe!r}; available: {avail}"
    # stream only what callers can use - the cwd tree is operator-extendable,
    # and a multi-GB planted list must not be buffered whole
    words: list[str] = []
    try:
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                w = line.strip()
                if w and not w.startswith("#"):
                    words.append(w)
                if len(words) >= limit:
                    break
    except OSError as exc:
        return [], f"wordlist {safe!r} unreadable: {exc}"
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
    max_words = _ival(max_words, 80, 1, 400)
    words, err = _load_wordlist(wordlist, limit=max_words)
    if err:
        return {"error": err}
    keep = None
    statuses = str(statuses or "")
    if statuses.strip():
        keep = {int(s) for s in re.split(r"[^0-9]+", statuses) if s}
    sep = "&" if "?" in base_url else "?"
    method = str(method or "GET").upper()
    data = data if isinstance(data, str) else (None if data is None else str(data))
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
    """All manifest dirs, user tree first (it shadows bundled ids).
    The cwd tree is only searched under ARGUS_EXPLOITS_CWD=1."""
    seen, out = set(), []
    roots = (EXPLOITS_USER, EXPLOITS) \
        if os.environ.get("ARGUS_EXPLOITS_CWD") == "1" else (EXPLOITS,)
    for root in roots:
        if not root.exists():
            continue
        for d in sorted(root.iterdir()):
            if d.is_dir() and (d / "manifest.json").exists() \
                    and d.name not in seen:
                seen.add(d.name)
                out.append(d)
    return out


def _load_manifest(exploit_id: str) -> tuple[dict | None, Path | None, str | None]:
    safe = re.sub(r"[^a-z0-9_-]", "", str(exploit_id or "").lower())
    roots = (EXPLOITS_USER, EXPLOITS) \
        if os.environ.get("ARGUS_EXPLOITS_CWD") == "1" else (EXPLOITS,)
    for root in roots:
        d = root / safe
        mpath = d / "manifest.json"
        if mpath.exists():
            try:
                meta = json.loads(mpath.read_text(encoding="utf-8"))
                if not isinstance(meta, dict):
                    raise ValueError("manifest is not an object")
                return meta, d, None
            except (ValueError, OSError) as exc:
                return None, None, f"bad manifest for {safe!r}: {exc}"
    avail = sorted(d.name for d in _exploit_dirs())
    return None, None, f"no exploit {safe!r}; available: {avail}"


def list_exploits(ctx: Context) -> dict:
    out = []
    for d in _exploit_dirs():
        try:
            meta = json.loads((d / "manifest.json").read_text(
                encoding="utf-8"))
            if not isinstance(meta, dict):
                raise ValueError("manifest is not an object")
            out.append({"id": d.name, "title": meta.get("title", ""),
                        "affects": meta.get("affects", []),
                        "cve": meta.get("cve")})
        except (ValueError, OSError):
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
    if not isinstance(cmd_tpl, list) or not cmd_tpl:
        return {"error": "manifest 'command' is not a non-empty list"}
    cmd = [str(part).replace("{target}", target)
              .replace("{args}", str(args or ""))
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
    timeout_s = _ival(timeout_s, manifest.get("timeout_s", 60), 5, 300)
    try:
        # exploit PoCs are the least-trusted local code (often downloaded)
        # - scrub credentials from the environment they inherit: key names
        # matching the secret pattern AND any declared --secret value under
        # an innocuous name (run_external already does both)
        from ..mcp import MCPClient
        env = {k: v for k, v in os.environ.items()
               if not any(s in k.upper() for s in MCPClient._SECRET_RE)
               and v not in ctx.session.secret_values}
        from ._subproc import run_capped
        marker = manifest.get("proof_marker")
        marker = marker if isinstance(marker, str) else ""
        if marker:
            try:
                re.compile(marker.encode())
            except re.error:
                marker = ""
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
