"""Driving a real browser, for the half of XSS the bytes cannot show.

Reflection is visible in a response: the payload came back unencoded.
Execution is not - an entity-encoded payload and a live one can both carry
the same characters, and both reflect. Telling them apart needs something
that parses HTML the way a victim's browser does.

This drives `agent-browser`, an external CLI, the same way `analysis.py`
drives sqlmap and nuclei: found on PATH, never installed by this package,
and absent without breaking anything. It is not a dependency, and the
package still installs with no pip step.

What this module does NOT do is report whether the payload executed. It
navigates, and that is all. The browser's own answer to "did my script
run" would reach the gate through this process, and a probe's report of
its own success is the one thing `record_finding` refuses for every other
class. Execution is shown instead by what the payload DOES: it calls back
to `argus/collector.py`, and the collector records the hit off its own
socket. See that module for why the distinction carries the weight.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import time

__all__ = ["BROWSER_BIN", "available", "visit", "why_unavailable"]

# The npm package name is the binary name. `AGENT_BROWSER_BIN` overrides it
# for a local install (`./node_modules/.bin/agent-browser`), which is how it
# arrives when nobody has installed it globally.
BROWSER_BIN = "agent-browser"

_NAV_TIMEOUT = 90
# A payload that executes fetches immediately, but the navigation command
# returns as soon as the page is loaded, which can be before a deferred or
# event-driven payload has run. This is how long to keep listening after
# that. It bounds a wait, it does not bound the proof: a callback that
# arrives is graded on its timestamp, not on having arrived inside a window.
SETTLE_SECONDS = 3.0


def available() -> str:
    """The browser binary's path, or "" when there is none."""
    override = os.environ.get("AGENT_BROWSER_BIN", "").strip()
    if override:
        return override if os.path.isfile(override) and os.access(override, os.X_OK) else ""
    return shutil.which(BROWSER_BIN) or ""


def why_unavailable() -> str:
    """One line a verdict can carry, so "no browser" says what to do."""
    return (f"`{BROWSER_BIN}` is not on PATH. It is an external tool, like "
            f"sqlmap and nuclei - `npm i -g {BROWSER_BIN}`, or set "
            f"AGENT_BROWSER_BIN to a local install. Without it a reflected "
            f"payload can be shown to reflect but not to execute.")


def visit(url: str, timeout: int = _NAV_TIMEOUT) -> dict:
    """Navigate to `url` and return what the CLI said.

    The return value is for the transcript and for diagnosing a failed run.
    It is deliberately NOT evidence: nothing in `proof.py` reads it, because
    a tool's account of its own run is what the gate exists to not take.
    """
    binary = available()
    if not binary:
        return {"ok": False, "reason": why_unavailable(), "stdout": "",
                "stderr": "", "seconds": 0.0}
    started = time.time()
    try:
        proc = subprocess.run([binary, "open", url], capture_output=True,
                              text=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return {"ok": False, "reason": f"navigation exceeded {timeout}s",
                "stdout": "", "stderr": "", "seconds": round(time.time() - started, 2)}
    except OSError as exc:
        return {"ok": False, "reason": f"could not run {binary}: {exc}",
                "stdout": "", "stderr": "", "seconds": round(time.time() - started, 2)}
    return {
        "ok": proc.returncode == 0,
        "reason": "" if proc.returncode == 0 else f"exit {proc.returncode}",
        # Bounded: the page's own text can come back here, and a transcript
        # entry is not the place for a megabyte of target-controlled bytes.
        "stdout": (proc.stdout or "")[:4000],
        "stderr": (proc.stderr or "")[:2000],
        "seconds": round(time.time() - started, 2),
    }


def close(timeout: int = 30) -> None:
    """Shut the browser down. Failure here is not worth failing a probe for."""
    binary = available()
    if not binary:
        return
    try:
        subprocess.run([binary, "close"], capture_output=True, text=True,
                       timeout=timeout, check=False)
    except (subprocess.TimeoutExpired, OSError):
        return
