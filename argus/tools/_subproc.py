"""Bounded subprocess capture: stdout/stderr land in temp files, not memory.

A runaway scanner or exploit PoC printing gigabytes used to exhaust memory
via subprocess.run(capture_output=True) before the result string was ever
sliced. Redirecting to temp files bounds memory by disk instead - we read
back only the head (transcript) and tail (model view) we actually keep.
"""
from __future__ import annotations

import os
import re
import signal
import subprocess
import tempfile


def _kill_tree(proc: subprocess.Popen, pgid: int | None = None) -> None:
    """Kill the child AND anything it spawned.

    `subprocess.run(..., timeout=)` sends SIGKILL to the direct child only
    and then waits for it. Anything that child spawned survives, is
    reparented to init, and keeps the inherited stdout fd - a temp file
    already unlinked, so it grows with no visible file - along with its
    network access.

    For this system that is not a tidiness problem. The orphan goes on
    talking to the target with no ScopeGuard, no RateLimiter and no request
    budget, nothing it does reaches the transcript, and the engagement's
    own record says the run was stopped after N seconds. Every claim this
    package makes about bounding what it sends is false for the lifetime of
    that process.

    On POSIX the child is started with `start_new_session=True`, so it
    leads its own process group and the group can be signalled as a unit.
    On Windows `taskkill /T` walks the child tree by pid. Both fall back to
    killing the direct child, which is what the old behaviour was, so a
    platform where neither works is no worse off than before.
    """
    try:
        if os.name == "posix":
            # `pgid` is for a caller that has already reaped the leader.
            # `os.getpgid` needs a live pid, so a caller that waits first
            # and asks second gets ProcessLookupError and signals nobody -
            # which is how `MCPClient.close` left a whole tree running
            # after a perfectly successful `terminate()` + `wait()`.
            target = pgid if pgid is not None else os.getpgid(proc.pid)
            # ...and never our OWN group. Every caller here starts its
            # child with `start_new_session=True`, so the group holds the
            # child's tree and nothing else - but that is one line away in
            # a different file, and if the two ever part company this
            # function SIGKILLs the agent that called it. Found by planting
            # exactly that: with the session flag removed from
            # `MCPClient._start`, `close()` took the whole pytest process
            # down with it, exit 137. Falling through to `proc.kill()` is
            # the behaviour this helper replaced, so the degraded path is
            # no worse than not having it.
            if target == os.getpgid(0):
                raise RuntimeError(
                    "refusing to signal our own process group: the child "
                    "was not started in a session of its own, so the group "
                    "contains this process")
            os.killpg(target, signal.SIGKILL)
            return
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       stdin=subprocess.DEVNULL, timeout=10)
        return
    except Exception:                       # pragma: no cover - platform dep
        pass
    try:
        proc.kill()
    except Exception:                       # pragma: no cover
        pass


def run_capped(cmd: list[str], timeout_s: float, cwd: str | None = None,
               env: dict | None = None,
               needle: str | None = None) -> tuple[int, str, str, bool]:
    """Run cmd; return (returncode, head_text, tail_text, needle_found).

    head_text: first bytes of stdout + first bytes of stderr (audit view).
    tail_text: last bytes of each stream (model view - scanner summaries
    and proof markers live at the end).
    needle: optional regex - searched across BOTH full streams so a proof
    marker in the middle of a huge output is still caught."""
    with tempfile.TemporaryFile(mode="w+b") as fo, \
            tempfile.TemporaryFile(mode="w+b") as fe:
        # stdin=DEVNULL, not inherited. Under `argus mcp-serve` the agent's
        # stdin IS the host's JSON-RPC channel: an external tool that reads it
        # - sqlmap prompting, curl with no URL, anything interactive - consumes
        # the host's frames and the session wedges with no error anywhere.
        # A pentest tool has no business reading our stdin in any mode.
        # `Popen` rather than `run`, so the timeout path can kill the whole
        # tree instead of one pid. `start_new_session` makes the child a
        # process-group leader on POSIX; see `_kill_tree`.
        extra = {"start_new_session": True} if os.name == "posix" else {}
        proc = subprocess.Popen(cmd, stdout=fo, stderr=fe,
                                stdin=subprocess.DEVNULL, cwd=cwd, env=env,
                                **extra)
        try:
            proc.wait(timeout=timeout_s)
        except subprocess.TimeoutExpired:
            _kill_tree(proc)
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:   # pragma: no cover
                pass
            # the contract callers depend on is unchanged: `analysis.py`
            # turns this into {"error": "timed out after Ns"}
            raise
        so_size, se_size = fo.tell(), fe.tell()

        def _rd(tf, off: int, n: int) -> str:
            tf.seek(off)
            return tf.read(n).decode("utf-8", "replace")

        head = _rd(fo, 0, 45_000)
        shead = _rd(fe, 0, 5_000)
        tail = _rd(fo, max(0, so_size - 15_000), 15_000)
        stail = _rd(fe, max(0, se_size - 5_000), 5_000)
        found = False
        if needle:
            rx = re.compile(needle.encode())
            for tf in (fo, fe):
                tf.seek(0)
                overlap = b""
                while chunk := tf.read(65536):
                    window = overlap + chunk
                    if rx.search(window):
                        found = True
                        break
                    # markers are short; a 4K carry-over catches matches
                    # straddling the read boundary
                    overlap = window[-4096:]
                if found:
                    break
    head_full = head + ("\n[stderr]\n" + shead if shead else "")
    tail_full = tail + ("\n[stderr]\n" + stail if stail else "")
    return proc.returncode, head_full, tail_full, found
