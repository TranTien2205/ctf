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
