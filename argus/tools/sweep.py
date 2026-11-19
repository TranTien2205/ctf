"""The hybrid recon fan-out, exposed to the agent.

`argus/orchestrator.py` runs several scanners at once and merges what they
found. It was written, tested and then imported by nothing: 1500 lines no
engagement could reach. This is the adapter that puts it on the tool table.

WHERE THE AGENT HALF WENT. The orchestrator takes an injected `agent_fn` so
its second pass can ask a model for more paths to try. In an engagement the
model IS the caller of this tool, so wiring `agent_fn` back into it would
re-enter the agent loop from inside a tool call. The hybrid is realised one
level up instead, and it is the same hybrid:

    sweep(url)                      -> what the scanners found, with the
                                       shapes they found it in
    ...the model reads the patterns and writes candidates...
    sweep(url, wordlist="a\nb\nc")  -> the scanners run again with them

That is the operator's point - a scanner is only as good as the wordlist you
already have, and a model can write one from what just came back - with the
model doing the generating in its own turn, where its reasoning is recorded
in the transcript rather than buried in a subprocess.

EVERY RUN IS RECORDED. A scanner's output is evidence about the target and
belongs on the record, not only in the reply to the model. Each invocation
lands in the transcript as its own entry, so a finding can cite the sweep
that found the endpoint.
"""

from __future__ import annotations

import shlex

from .. import orchestrator
from . import wordlist_agent as _wl
from .registry import Context, _ival

# What the model may ask for. The orchestrator refuses anything else, but
# naming the set here lets the refusal say so before a subprocess is planned.
SWEEP_TOOLS = ("nmap", "ffuf", "nuclei")

# A model-written wordlist is derived from bytes the target chose, so it is
# bounded the same way any other target-influenced input is.
MAX_WORDS = 400
MAX_WORD_LEN = 120


def _clean_wordlist(raw: str) -> tuple[list[str], list[str]]:
    """Split a model-supplied wordlist, dropping what cannot be a path.

    Returns (words, refused). Refusals are reported rather than silently
    dropped: a caller that asked for 300 words and got 40 should be told
    which 260 went and why, or it will keep sending them.
    """
    words, refused = [], []
    for line in str(raw or "").splitlines():
        word = line.strip()
        if not word:
            continue
        if len(words) >= MAX_WORDS:
            refused.append(f"{word[:40]!r}: over the {MAX_WORDS}-word cap")
            continue
        if len(word) > MAX_WORD_LEN:
            refused.append(f"{word[:40]!r}: longer than {MAX_WORD_LEN} characters")
            continue
        if word.startswith("-"):
            # ffuf takes a value beginning with '-' as the next option, so a
            # word like `-oOUT` would turn a scan into a file write.
            refused.append(f"{word[:40]!r}: reads as a command-line flag")
            continue
        if any(c in word for c in "\r\n\x00"):
            refused.append(f"{word[:40]!r}: contains a control character")
            continue
        words.append(word)
    return words, refused


def _record(ctx: Context, target: str, run) -> str:
    """One scanner invocation, on the record.

    Recorded as an exchange rather than an event so that `read_response` can
    reach the output and a finding can cite it. The "request" is the command
    line, because that is what was sent; the "response" is what came back.
    """
    request = {
        "direction": "outbound",
        "method": "EXEC",
        "url": target,
        "argv": list(run.argv),
        "headers": {},
        "body": shlex.join(run.argv) if run.argv else "",
    }
    response = {
        "status": 0 if run.skipped_reason else (run.rc if run.rc is not None else -1),
        "headers": {"x-seconds": str(run.seconds)},
        "body": run.stdout or "",
        "stderr": (run.stderr or "")[:4000],
    }
    note = run.skipped_reason or f"{run.tool} rc={run.rc} in {run.seconds}s"
    return ctx.session.record_exchange(
        "recon_sweep", request, response, note=note,
        agent=getattr(ctx, "agent_name", "") or "")



def _agent_half(ctx):
    """`(agent_fn, note)` for the hybrid's agent half, built HERE.

    Built on this thread deliberately: the credential resolution it triggers
    writes a temp file named only by PID and replaces the operator's real
    credentials file, so doing it from one of the orchestrator's worker
    threads would race on that path. The orchestrator then calls the
    returned object from a daemon thread, which is safe because
    `WordlistAgent` locks everything it mutates.
    """
    agent, why = _wl.make_agent_fn(getattr(ctx, "cfg", None))
    return agent, why


def _agent_report(agent, why: str, result) -> dict:
    """What the model reads about the agent half - both halves of the fact.

    MEASURED, and this is the whole reason this function exists: with no
    credential configured, `make_agent_fn` still returns an agent (the
    client constructs fine; the CALL is what fails), so the orchestrator
    sees an empty string and reports `agent_ran=False` with the note
    "agent_fn returned no text". That reads as "the model ran and had
    nothing to say" when the truth is "the model was never reached". The
    reason lives in the agent's own stats, so it has to be surfaced or the
    operator never learns a key is missing - a refusal reading as an empty
    result, one layer up from the usual place.
    """
    out = {"agent_ran": bool(getattr(result, "agent_ran", False)),
           "agent_note": str(getattr(result, "agent_note", "") or ""),
           "agent_suggestions": list(getattr(result, "agent_suggestions", []))[:60]}
    if agent is None:
        out["agent_half"] = {"available": False, "reason": why}
        return out
    stats = agent.stats()
    out["agent_half"] = {"available": True, **stats}
    if stats.get("failures") and not stats.get("calls"):
        # Replace, not append: the orchestrator's note is accurate about
        # what it saw and wrong about what happened.
        out["agent_note"] = (
            f"the agent half could not reach {stats['model']}: "
            f"{stats.get('last_error', 'the call failed')}. The tool half's "
            "results above stand on their own; this is not a finding about "
            "the target.")
    return out


def _record_agent_exchanges(ctx, agent, target: str) -> list[str]:
    """Put the model's prompt and reply in the transcript.

    The agent half's contribution is reasoning that changed what was
    scanned, so it belongs on the record beside the scanner runs that acted
    on it - otherwise a second ffuf pass appears with no account of where
    its words came from.
    """
    ids: list[str] = []
    for prompt, reply in list(getattr(agent, "exchanges", []) or []):
        try:
            rid = ctx.session.record_exchange(
                "wordlist_agent",
                {"method": "AGENT", "url": target,
                 "headers": {"x-argus-model": agent.model},
                 "body": prompt[:8000]},
                {"status": 200, "headers": {}, "body": reply[:4000]},
                note="the agent half's candidates for this sweep")
            ids.append(rid)
        except Exception:                       # noqa: BLE001
            break
    return ids

def recon_sweep(ctx: Context, url: str, tools: str = "", wordlist: str = "",
          timeout_s: int = 180) -> dict:
    """Run the installed scanners against one in-scope URL, concurrently."""
    target = str(url or "").strip()
    if not target:
        return {"error": "url is required"}

    wanted = [t.strip().lower() for t in str(tools or "").replace(",", " ").split()]
    unknown = [t for t in wanted if t not in SWEEP_TOOLS]
    if unknown:
        return {"error": f"this tool drives {list(SWEEP_TOOLS)}; "
                         f"{unknown} is not one of them. For anything else use "
                         f"run_external, which applies its own per-tool guards."}

    words, refused_words = _clean_wordlist(wordlist)
    listfile = ""
    if words:
        import tempfile
        fd, listfile = tempfile.mkstemp(prefix="argus-words-", suffix=".txt",
                                        dir=str(ctx.session.dir))
        with open(fd, "w", encoding="utf-8") as fh:
            fh.write("\n".join(words) + "\n")

    # The agent half, built on THIS thread (see `_agent_half`). The
    # orchestrator starts it concurrently with the scanners that are still
    # running and turns its words into a second ffuf pass. MEASURED on the
    # lab: one ffuf run found 6 endpoints alone and 10 with the agent half
    # supplying five words - /api-docs, /api-docs/, /ftp and /rest added,
    # none lost. It is additive by construction: the agent contributes a
    # wordlist, and a wordlist can only find more paths.
    agent, agent_why = _agent_half(ctx)
    try:
        result = orchestrator.recon_sweep(
            target,
            scope=ctx.scope,
            workdir=str(ctx.session.dir),
            tools=wanted or None,
            agent_fn=agent,
            timeout_s=_ival(timeout_s, 180, 20, 600),
            wordlist=listfile,
        )
    except Exception as exc:        # noqa: BLE001
        return {"error": f"the sweep could not run: {exc}"}

    runs = []
    for run in result.tool_runs:
        rid = _record(ctx, target, run)
        runs.append({
            "request_id": rid,
            "tool": run.tool,
            "rc": run.rc,
            "seconds": run.seconds,
            "skipped": run.skipped_reason,
            # The model reads the endpoints below; the raw output stays in
            # the transcript, reachable with read_response(request_id).
            "output_chars": len(run.stdout or ""),
        })

    out = {
        "target": result.target,
        "endpoints": result.endpoints[:200],
        "endpoint_count": len(result.endpoints),
        "runs": runs,
        "seconds": result.seconds,
        "note": ("Hybrid: the scanners ran on the wordlist, and the agent "
                 "half ran concurrently on the shapes they returned, its "
                 "words becoming a second ffuf pass. Read `agent_half` for "
                 "whether that half was reached and what it cost. You can "
                 "still drive it yourself: call again with `wordlist=` to "
                 "add candidates of your own."),
    }
    out.update(_agent_report(agent, agent_why, result))
    if agent is not None:
        ids = _record_agent_exchanges(ctx, agent, target)
        if ids:
            out["agent_request_ids"] = ids
    if words:
        out["wordlist_words"] = len(words)
    if refused_words:
        out["wordlist_refused"] = refused_words[:20]
    # MEASURED: an out-of-scope target produced `endpoint_count: 0` and the
    # verdict "no endpoint came back ... the wordlist did not name it". The
    # orchestrator had refused correctly and spawned nothing - the refusal
    # was sitting in each run's `skipped` field - but the sentence the model
    # reads said the target was empty. A model told that widens its wordlist
    # and tries again forever instead of learning its target is out of
    # scope. A refusal is a decision and has to be the headline, not a
    # per-run detail under a summary that contradicts it.
    skipped = [r for r in runs if r["skipped"]]
    refused = [r for r in skipped if "scope" in r["skipped"].lower()]
    if refused:
        out["refused"] = True
        out["verdict"] = (
            "NOTHING WAS SCANNED. The scope guard refused this target before "
            "any process started: " + refused[0]["skipped"] + ". This is not "
            "a result about the target - change the request or the scope; do "
            "not retry it as written.")
    elif skipped and len(skipped) == len(runs):
        out["refused"] = True
        out["verdict"] = (
            "NOTHING WAS SCANNED. Every tool was skipped: " +
            "; ".join(r["tool"] + " - " + r["skipped"] for r in skipped[:3]) +
            ". An empty endpoint list here says nothing about the target.")
    elif not result.endpoints:
        out["verdict"] = ("the scanners ran and no endpoint came back. Either "
                          "nothing is there, or the wordlist did not name it - "
                          "those are different, and only the second one you "
                          "can fix.")
    return out


#: What `exploit_fanout` drives. Separate from `SWEEP_TOOLS` because these
#: are the ones that send payloads rather than enumerate: naming them here
#: keeps the error message honest about what this tool can and cannot run.
FANOUT_TOOLS = ("curl", "nuclei", "sqlmap")

#: The orchestrator caps the list at 500 and the parallelism at 16. This cap
#: is smaller because a model picks the list: an engagement that wants 200
#: endpoints swept at once is a decision for an operator, not a tool call.
MAX_FANOUT_ENDPOINTS = 24


def fanout_sweep(ctx: Context, endpoints: str = "", timeout_s: int = 180,
                  max_parallel: int = 4) -> dict:
    """Work several confirmed endpoints concurrently, one result each.

    The other half of `argus/orchestrator.py`, and the fourth orphan this
    session found: `exploit_fanout` was written, tested and reached by
    nothing - a repo-wide audit for public functions with no caller anywhere
    in the package returned it and one other.

    `recon_sweep` enumerates ONE url. This takes a list and fans out, each
    endpoint in its own directory, because sqlmap keys its session files by
    target host and two endpoints on one host would otherwise share a
    session directory and corrupt each other's state.

    Every endpoint is scope-checked inside its own sweep before any process
    exists, so an out-of-scope entry in the list refuses itself rather than
    taking the call down.
    """
    raw = [e.strip() for e in str(endpoints or "").replace(",", "\n").split("\n")]
    eps, seen, refused = [], set(), []
    for ep in raw:
        if not ep or ep in seen:
            continue
        if not ep.lower().startswith(("http://", "https://")):
            refused.append({"endpoint": ep[:120],
                            "reason": "not an http(s) URL"})
            continue
        seen.add(ep)
        eps.append(ep)
        if len(eps) >= MAX_FANOUT_ENDPOINTS:
            refused.append({"endpoint": "...",
                            "reason": f"list capped at {MAX_FANOUT_ENDPOINTS} "
                                      "endpoints per call"})
            break
    if not eps:
        return {"error": "no usable endpoint; pass full http(s) URLs, one per "
                         "line or comma-separated",
                "refused": refused}

    agent, agent_why = _agent_half(ctx)
    try:
        results = orchestrator.exploit_fanout(
            # `target` is context for the agent prompt and is never dialled -
            # the orchestrator's own docstring says so, and `agent_fn` is
            # None here, so nothing reads it. `ScopeGuard` exposes no
            # `.target`, and a `hasattr` dance implying one would be a
            # sentence that gets believed. The first endpoint, plainly.
            eps[0],
            eps,
            scope=ctx.scope,
            workdir=str(ctx.session.dir),
            # ONE agent_fn shared by up to `max_parallel` concurrent sweeps,
            # each calling it from its own daemon thread. That is why
            # `WordlistAgent` locks everything it mutates: a fan-out is
            # shared mutable state by construction. MEASURED with three
            # endpoints: three calls, three distinct thread ids, all
            # starting within 0.53s of each other, and the whole fan-out
            # finishing in 37.9s rather than three times that.
            agent_fn=agent,
            timeout_s=_ival(timeout_s, 180, 20, 600),
            max_parallel=_ival(max_parallel, 4, 1, 8),
        )
    except Exception as exc:        # noqa: BLE001
        return {"error": f"the fan-out could not run: {exc}"}

    per, scanned, all_refused = [], 0, []
    for result in results:
        runs = []
        for run in result.tool_runs:
            rid = _record(ctx, result.target, run)
            runs.append({"request_id": rid, "tool": run.tool, "rc": run.rc,
                         "seconds": run.seconds,
                         "skipped": run.skipped_reason,
                         "output_chars": len(run.stdout or "")})
            if run.skipped_reason and "scope" in run.skipped_reason.lower():
                # One entry per ENDPOINT, not per tool. The guard refuses
                # before each tool starts, so a three-tool sweep of one
                # out-of-scope endpoint produced the same line three times
                # and read as three problems.
                if not any(x["endpoint"] == result.target for x in all_refused):
                    all_refused.append({"endpoint": result.target,
                                        "reason": run.skipped_reason})
            elif not run.skipped_reason:
                scanned += 1
        per.append({"endpoint": result.target, "runs": runs,
                    "endpoints": result.endpoints[:50],
                    "seconds": result.seconds})

    out = {"requested": len(eps), "results": per,
           "tools": list(FANOUT_TOOLS)}
    # Per endpoint, because each sweep ran its own agent call and one of
    # them reaching the model while another did not is a fact about the run.
    out["agent_ran_per_endpoint"] = {
        str(getattr(r, "target", "")): bool(getattr(r, "agent_ran", False))
        for r in results}
    if agent is None:
        out["agent_half"] = {"available": False, "reason": agent_why}
    else:
        out["agent_half"] = {"available": True, **agent.stats()}
        ids = _record_agent_exchanges(ctx, agent, eps[0])
        if ids:
            out["agent_request_ids"] = ids
    if refused:
        out["not_submitted"] = refused
    if all_refused:
        out["scope_refused"] = all_refused
    # Same defect shape `recon_sweep` was fixed for: a refusal must not read
    # as an empty result. If nothing was scanned at all, that is the verdict,
    # not a count of zero findings.
    if scanned == 0:
        reason = (all_refused[0]["reason"] if all_refused
                  else "every tool was skipped - check which are installed")
        out["refused"] = bool(all_refused)
        out["verdict"] = ("NOTHING WAS SCANNED across "
                          f"{len(eps)} endpoint(s): {reason}. Do not widen "
                          "the endpoint list; this is not a result about the "
                          "target.")
    else:
        out["verdict"] = (f"{scanned} tool run(s) completed across "
                          f"{len(eps)} endpoint(s). Cite a run's request_id "
                          "for anything you claim from its output; the raw "
                          "output is in the transcript via read_response.")
    return out
