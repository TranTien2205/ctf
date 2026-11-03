"""Running an external command without giving a model a shell.

Four properties, each one load-bearing:

* **argv only.** There is no `shell=True` anywhere in this system. A model that
  writes `; rm -rf /` into a parameter produces a tool argument, not a command.
* **a timeout that actually kills.** The child runs in its own session, so a
  timeout kills the whole process group rather than leaving `nmap` orphaned.
* **bounded output.** `nuclei` against a large surface will happily emit tens of
  megabytes. The cap is applied before the text is stored or shown.
* **an audit line per command.** Argv, exit code, duration and digest, appended
  to the engagement's `log/commands.jsonl` whether the command worked or not.
"""
from __future__ import annotations

import os
import shutil
import signal
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from .. import config
from ..util import append_jsonl, bound, now_iso, redact, sha256_text


class ToolMissing(RuntimeError):
    """A tool the caller asked for is not installed. Named, with the install hint."""


INSTALL_HINTS = {
    "nmap": "apt install nmap",
    "masscan": "apt install masscan",
    "httpx": "apt install httpx-toolkit  (the ProjectDiscovery one, not the python library)",
    "whatweb": "apt install whatweb",
    "subfinder": "apt install subfinder",
    "ffuf": "apt install ffuf",
    "feroxbuster": "apt install feroxbuster",
    "gobuster": "apt install gobuster",
    "nuclei": "apt install nuclei && nuclei -update-templates",
    "nikto": "apt install nikto",
    "sqlmap": "apt install sqlmap",
    "wpscan": "apt install wpscan",
    "curl": "apt install curl",
    "katana": "go install github.com/projectdiscovery/katana/cmd/katana@latest",
    "gau": "go install github.com/lc/gau/v2/cmd/gau@latest",
}


def which(tool: str) -> str | None:
    return shutil.which(tool)


def require(tool: str) -> str:
    path = which(tool)
    if path is None:
        hint = INSTALL_HINTS.get(tool, f"install {tool} and put it on PATH")
        raise ToolMissing(f"{tool} is not installed: {hint}")
    return path


@dataclass
class CommandResult:
    argv: list[str]
    exit_code: int | None
    stdout: str
    stderr: str
    duration_ms: int
    timed_out: bool = False
    truncated: bool = False
    started: str = field(default_factory=now_iso)

    @property
    def ok(self) -> bool:
        return self.exit_code == 0 and not self.timed_out

    def text(self, limit: int = config.OBSERVATION_CAP) -> str:
        """What a model is shown: stdout, then stderr, both bounded."""
        parts = []
        if self.stdout.strip():
            parts.append(bound(self.stdout, limit, tail=1000))
        if self.stderr.strip():
            parts.append("--- stderr ---\n" + bound(self.stderr, min(limit // 4, 3000)))
        if self.timed_out:
            parts.append(f"--- the command was killed after the timeout; "
                         f"output above is what it had produced by then ---")
        return "\n".join(parts) or f"(no output, exit {self.exit_code})"

    def to_dict(self) -> dict:
        return {"argv": self.argv, "exit_code": self.exit_code, "duration_ms": self.duration_ms,
                "timed_out": self.timed_out, "truncated": self.truncated,
                "stdout_sha256": sha256_text(self.stdout)}


def run(argv: list[str], timeout: int = config.TOOL_TIMEOUT_DEFAULT, stdin: str | None = None,
        cwd: str | os.PathLike[str] | None = None, env_extra: dict | None = None,
        output_cap: int = config.TOOL_OUTPUT_CAP, log_path: Path | None = None) -> CommandResult:
    if not argv or not isinstance(argv, list):
        raise ValueError("argv must be a non-empty list; this runner never takes a command string")
    argv = [str(a) for a in argv]
    require(os.path.basename(argv[0]) if os.sep not in argv[0] else argv[0])
    timeout = max(1, min(int(timeout), config.TOOL_TIMEOUT_MAX))
    env = dict(os.environ)
    env.pop("ANTHROPIC_API_KEY", None)        # a pentest tool never needs our model keys
    env.pop("OPENAI_API_KEY", None)
    env.pop("DEEPSEEK_API_KEY", None)
    env.pop("GEMINI_API_KEY", None)
    if env_extra:
        env.update({str(k): str(v) for k, v in env_extra.items()})

    started = time.monotonic()
    timed_out = False
    # Popen rather than subprocess.run, for one reason: on a timeout we need the
    # child's pid so we can signal its whole process group. `run` only hands back
    # the exception, and an earlier version of this file reaped by name with
    # `pkill -f`, which matched the parent shell and killed it. Kill the group you
    # started, never a pattern.
    process = subprocess.Popen(
        argv, stdin=subprocess.PIPE if stdin else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(cwd) if cwd else None, env=env, start_new_session=True,
    )
    try:
        out, err = process.communicate(input=stdin.encode() if stdin else None, timeout=timeout)
        code = process.returncode
    except subprocess.TimeoutExpired:
        timed_out = True
        _kill_group(process)
        try:
            out, err = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            out, err = b"", b""
        err = (err or b"") + f"\n[killed after {timeout}s]".encode()
        code = None

    duration = int((time.monotonic() - started) * 1000)
    stdout = (out or b"").decode("utf-8", "replace")
    stderr = (err or b"").decode("utf-8", "replace")
    truncated = len(stdout) > output_cap or len(stderr) > output_cap
    result = CommandResult(argv, code, redact(bound(stdout, output_cap, tail=4000)),
                           redact(bound(stderr, output_cap // 4)), duration, timed_out, truncated)
    if log_path is not None:
        append_jsonl(log_path, {"ts": result.started, **result.to_dict()})
    return result


def _kill_group(process: "subprocess.Popen") -> None:
    """SIGTERM the child's session, then SIGKILL what ignored it."""
    try:
        group = os.getpgid(process.pid)
    except OSError:
        return
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(group, sig)
        except OSError:
            return
        for _ in range(20):
            if process.poll() is not None:
                return
            time.sleep(0.05)


def signal_name(code: int | None) -> str:
    if code is None or code >= 0:
        return ""
    try:
        return signal.Signals(-code).name
    except ValueError:
        return ""
