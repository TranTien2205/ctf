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

    try:
        result = orchestrator.recon_sweep(
            target,
            scope=ctx.scope,
            workdir=str(ctx.session.dir),
            tools=wanted or None,
            agent_fn=None,          # see the module docstring
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
        # Never claim an agent half ran. It did not: this tool runs scanners,
        # and the generating half is the caller's next turn.
        "agent_ran": False,
        "note": ("Scanners only. To do the other half, read the shapes above, "
                 "write candidates they suggest, and call sweep again with "
                 "wordlist= - that pass is yours, and it is recorded as your "
                 "reasoning rather than hidden in a subprocess."),
    }
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
