"""run_external: the allowlist + arg guards get plenty of coverage in
selftest; these exercise the subprocess path itself (unpack, env scrub).
"""
import shutil
import sys

import argus.tools.analysis as analysis
from argus.tools.analysis import run_external
import argus.tools._subproc as _subproc


def test_run_external_returns_result(ctx, monkeypatch):
    """The 4-tuple from run_capped must unpack cleanly - a stray unpack
    bug turns every external call into a ValueError."""
    monkeypatch.setattr(shutil, "which", lambda t: sys.executable)
    out = run_external(ctx, "curl", "-V")   # python -V exits 0 with output
    assert "cmd_id" in out and out["returncode"] == 0
    assert "Python" in out["output"]


def test_run_external_env_scrubbed(ctx, monkeypatch):
    """Scanner children must not inherit credential env vars."""
    seen = {}

    def fake_run(cmd, timeout_s, cwd=None, env=None, needle=None):
        seen["env"] = dict(env or {})
        return 0, "h", "t", False

    monkeypatch.setattr(_subproc, "run_capped", fake_run)
    monkeypatch.setattr(shutil, "which", lambda t: "/bin/curl")
    monkeypatch.setenv("MY_TEST_API_KEY_42", "leakme")
    monkeypatch.setenv("PLAIN_VAR", "kept")
    ctx.session.secret_values.add("declared-secret-value")
    monkeypatch.setenv("ODD_NAME", "declared-secret-value")
    out = run_external(ctx, "curl", ctx.cfg.target)
    assert "cmd_id" in out
    env = seen["env"]
    assert "MY_TEST_API_KEY_42" not in env     # name pattern scrubbed
    assert "ODD_NAME" not in env               # declared-value scrubbed
    assert env.get("PLAIN_VAR") == "kept"


def test_run_external_rejects_unlisted(ctx):
    out = run_external(ctx, "nmap-evil", ctx.cfg.target)
    assert "error" in out


def test_the_timeout_kills_what_the_tool_spawned_not_just_the_tool():
    """`subprocess.run(timeout=)` kills one pid; children survive it.

    On TimeoutExpired CPython sends SIGKILL to the direct child and waits
    for it. Anything that child spawned is reparented to init and keeps
    the stdout fd it inherited - a temp file this module has already
    unlinked, so it grows with no visible file - along with its network
    access.

    For this package that is not tidiness. The orphan goes on talking to
    the target with no ScopeGuard, no RateLimiter and no request budget,
    nothing it does reaches the transcript, and the engagement's own
    record says the run was stopped after N seconds. Every claim argus
    makes about bounding what it sends is false for that process's
    lifetime.

    Measured both ways before the fix went in: with `subprocess.run` the
    grandchild's marker file appears after the run reports a timeout; with
    the process group killed it never appears.
    """
    import os
    import subprocess
    import tempfile
    import time

    import pytest

    if os.name != "posix":
        pytest.skip("process groups and `sh` are POSIX; CI covers nt "
                    "through the taskkill branch, which needs a real "
                    "Windows runner to exercise")

    marker = os.path.join(tempfile.mkdtemp(), "orphan-was-alive")
    # a child that spawns a grandchild due to touch the marker shortly,
    # then sleeps long enough that the timeout always fires first
    cmd = ["sh", "-c", f"( sleep 1; touch {marker} ) & sleep 30"]
    started = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired):
        _subproc.run_capped(cmd, timeout_s=0.5)
    # the contract callers depend on is unchanged: analysis.py turns this
    # into {"error": "timed out after Ns"}
    assert time.monotonic() - started < 5.0

    # THE MARGIN, STATED. The grandchild touches the marker 1s in and the
    # parent is killed at 0.5s, so this looks 5s in: a delay of up to 4s
    # still produces a red test. With the write at 2s and the look at 3s
    # the margin was 1 second, which a loaded runner can close - and this
    # assertion's only failure mode is passing wrongly, so a thin margin
    # here hides an orphan that still holds the target and the unlinked
    # stdout fd.
    time.sleep(5.0)
    assert not os.path.exists(marker), (
        "a process the timed-out tool spawned outlived the timeout: it "
        "still has the target, the unlinked stdout fd, and no place in "
        "the transcript")


def test_kill_tree_refuses_to_kill_the_agent_itself():
    """The degraded path has to degrade, not take the caller with it.

    `_kill_tree` SIGKILLs a process GROUP, which is only safe because
    every caller starts its child with `start_new_session=True` so the
    group holds that child's tree and nothing else. That flag is one line
    away in a different file from the signal, and if the two ever part
    company the group being signalled is the agent's own.

    Found by planting it: with the session flag removed from
    `MCPClient._start`, `close()` killed the whole pytest process, exit
    137 - no failure report, no output, just a dead runner, which is the
    least debuggable way for a test suite to tell you something.

    This test's assertion is that it reaches its own last line. A process
    that dies here cannot report anything, so the guard is checked by
    survival: the child must be dead and this process must not be.
    """
    import os
    import subprocess
    import sys

    import pytest

    if os.name != "posix":
        pytest.skip("process groups are POSIX")

    # deliberately NOT start_new_session: this child shares our group
    proc = subprocess.Popen([sys.executable, "-c",
                             "import time; time.sleep(30)"])
    try:
        assert os.getpgid(proc.pid) == os.getpgid(0), \
            "this test is meaningless unless the child shares our group"
        _subproc._kill_tree(proc)
        proc.wait(timeout=10)
    finally:
        if proc.poll() is None:
            proc.kill()
    # reached only if `_kill_tree` did not signal the group we are in
    assert proc.returncode is not None, "the child outlived _kill_tree"
