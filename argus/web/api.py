"""Data layer behind the operator dashboard: no HTTP, no framework.

Every function here takes plain values and returns plain data, so the API
contract can be driven in a test without a socket, and so `server.py` holds
nothing but routing, limits and headers. Standard library only.

Two rules shape this file:

* Runs are read from the session directory, never from memory alone. A run
  this server started also has a `web-run.json` sidecar for its state and
  event log, but the authoritative count of findings is always the length of
  `findings.json` on disk - a registry that reports its own bookkeeping
  would report what it intended rather than what happened.
* Nothing is claimed that was not observed. A directory that recorded no
  transcript entry is not a clean run, and a `running` state left behind by
  a server that exited is not a running run.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import threading
import time
import urllib.parse
from pathlib import Path
from typing import Callable

from .. import __version__
from ..scope import ScopeGuard
from ..session import Session, _redact_obj, sanitized_findings

# ---------------------------------------------------------------------------
# limits and names

#: Request bodies above this are refused: nothing over the cap is ever kept,
#: only discarded in fixed-size pieces so the caller can read the 413 (see
#: `server.DRAIN_LIMIT`). The console takes a target, an authorisation note
#: and a sentence of extra instruction; a megabyte is already three orders
#: of magnitude more than that, and reading an unbounded POST is the
#: cheapest way to exhaust a pentester's own box.
MAX_BODY = 1 << 20

#: Modes the console offers. `engagement` is the tier that needs an
#: authorisation note; `lab` is the local target. These are the fallback
#: values: when `argus.prompts` is importable its own definitions win, so
#: there is one list per concept rather than two that drift (see
#: `_prompts_module` and the three accessors below it).
MODES = ("lab", "engagement")

#: What a complete engagement authorisation must name when `argus.prompts`
#: is not available. `reference` is deliberately absent: a real
#: authorisation is often an email rather than a ticket, and requiring an id
#: pushes operators into typing a fake one.
REQUIRED_AUTH_FIELDS = ("authorised_by", "scope", "window")

#: States a run can be reported in. Anything else is a bug in this module.
RUN_STATES = ("queued", "running", "done", "failed", "blocked")

#: The four external tools the dashboard reports on. Kept in step with the
#: broker's allowlist by `_health_tools()` below - a health page that
#: advertises a tool `run_external` would refuse is a lie about capability.
HEALTH_TOOLS = ("nmap", "ffuf", "nuclei", "sqlmap")

#: Sidecar the web server writes beside the session artifacts. Deliberately
#: NOT one of the names `Session.seal_artifacts` digests (meta.json,
#: findings.json, notes.md, report.*, agent*.log, summary.json), so writing
#: it after a run was sealed cannot make `argus verify` fail.
WEB_STATE_FILE = "web-run.json"

#: Where the mode-specific prompt is written inside the run directory.
PROMPT_FILE = "prompt.txt"

#: Per-run event log cap. A long run must not grow a list until the server
#: dies; the transcript is the evidence store, this is a progress ticker.
EVENT_CAP = 500

#: Concurrent runs this server will start. Each run is a thread; an
#: unbounded POST loop would otherwise spawn threads until the box stops.
MAX_CONCURRENT_RUNS = 4

#: Runs one console will start in its whole lifetime. The concurrency cap
#: is not this: measured, 60 sequential POSTs went through in 0.7 s because
#: each run blocked instantly, so nothing throttled a POST loop and every
#: one of them left a session directory on disk - ~5000 a minute at the
#: measured rate. A stop, not a policy: restarting the console resets it,
#: and the CLI has no such limit.
MAX_RUNS_PER_SERVER = 500

#: In-memory records this registry keeps for runs it started. The
#: concurrency cap bounds how many run AT ONCE, which is not a bound on how
#: many are kept: measured, 60 sequential POST /api/runs (each blocked
#: instantly, so the semaphore never throttled) left 60 live records, 60
#: event lists and 60 dead Thread objects, none of them ever pruned. Beyond
#: this many, the oldest FINISHED records are dropped - `_persist` has
#: already written their state and event log to the sidecar, which both
#: `run_from_dir` and `events()` read back.
MAX_TRACKED_RUNS = 64

#: Bounds on operator free text arriving over HTTP.
MAX_TARGET_CHARS = 500
MAX_EXTRA_CHARS = 4000

#: Bounds on what the aggregate views return, so one directory of giant
#: artifacts cannot turn a dashboard refresh into a memory spike.
MAX_FINDING_ROWS = 2000
EXCERPT_CAP = 2000

#: Run rows one listing returns, newest first. `/api/runs` was already
#: 19.6 KB at 60 runs and nothing bounded it, so a dashboard poll grew with
#: the lifetime of the session directory - and `reports_rows`, which scans
#: the same list, had no cap of its own at all.
MAX_RUN_ROWS = 500

#: Session ids are `%Y%m%d-%H%M%S-<slugged host>` with an optional `-N`
#: suffix, and `session._slug` keeps only `[a-zA-Z0-9.-]` plus `_`. Anything
#: outside that is not an id this tree produced, and the id arrives in a URL.
_RUN_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}")

#: A transcript still being written this recently is reported as running
#: rather than failed. It is a measurement of the file, not a claim about a
#: process: the note says which.
LIVE_TRANSCRIPT_WINDOW_S = 180.0

#: A directory with no transcript entry recorded nothing, whatever any
#: other source claims about it. Named once because three places read the
#: same fact: `_derive_state`, the reconciliation at the end of
#: `run_from_dir`, and `RunRegistry._work`.
NOTE_NOTHING_RECORDED = "no transcript entries - nothing was recorded"

NOTE_NO_MODEL = (
    "no model credential found, so no agent ran: the tool half (nmap, ffuf, "
    "nuclei, sqlmap) can still be driven from the CLI against this target")
NOTE_NO_RUNNER = (
    "no runner is wired into this server: the run directory and its prompt "
    "were written, nothing was executed")
NOTE_STALE = (
    "the server exited while this run was in progress - its outcome was "
    "never recorded")
NOTE_RUNNER_NO_RECORD = (
    "the runner returned without recording a transcript entry - nothing was "
    "probed, so there is no evidence of a run")


class TooManyRuns(RuntimeError):
    """Raised by RunRegistry.create when the concurrency cap is reached."""


# ---------------------------------------------------------------------------
# small helpers


def _atomic_write(path: Path, text: str) -> None:
    """Write-rename, because a reader scans this directory while a worker
    thread writes it: a half-written sidecar must never be observable."""
    tmp = path.with_name(f"{path.name}.tmp-{os.getpid()}-{threading.get_ident()}")
    try:
        with tmp.open("w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)


_USERINFO_RE = re.compile(r"(?i)(https?://)([^/\s:@]{1,64}):([^/\s@]{1,256})@")


def _redact(text: str) -> str:
    """Mask `user:pass@` in anything that reaches an artifact or a response.

    The one URL an operator certainly types with a credential in it is the
    target, and an exception message or a tool banner quotes the URL back.
    `Session` already does this for its own artifacts; the event log is a
    second write path, so it needs the same gate.
    """
    return _USERINFO_RE.sub(r"\1\2:***@", str(text or ""))


def _read_json(path: Path, default):
    """Tolerant read: these files are operator-editable and a dashboard that
    500s on a hand-edited artifact is useless exactly when it is needed."""
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def _has_transcript_entry(path: Path) -> bool:
    """True if transcript.jsonl holds at least one record.

    Only existence is needed, so only the head is read: counting lines would
    make every dashboard refresh proportional to the size of every
    transcript in the directory.
    """
    try:
        with path.open("rb") as fh:
            head = fh.read(4096)
    except OSError:
        return False
    return any(line.strip().startswith(b"{") for line in head.splitlines())


# ---------------------------------------------------------------------------
# health


def _health_tools() -> dict[str, bool]:
    """Which of the four external tools are on PATH.

    Intersected with the broker's own allowlist rather than trusting this
    module's tuple: two lists naming one concept drift, and the dashboard
    must not advertise a tool `run_external` would refuse to launch.
    """
    try:
        from ..tools.analysis import _ALLOWED_TOOLS as allowed
    except Exception:  # pragma: no cover - import guard only
        allowed = set(HEALTH_TOOLS)
    return {name: bool(shutil.which(name)) and name in allowed
            for name in HEALTH_TOOLS}


def _credential_env_names() -> set[str]:
    names: set[str] = set()
    try:
        from ..config import _declared_key_envs
        names |= set(_declared_key_envs())
    except Exception:
        pass
    # the three Anthropic names explicitly, so this never depends on the
    # model catalogue parsing
    return names | {"ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN",
                    "CLAUDE_CODE_OAUTH_TOKEN"}


def credential_source_present() -> bool:
    """Is a model credential *source* present - env var or credential store.

    Presence, deliberately not validity. `config.resolve_auth` is the
    authoritative answer, and calling it from here would be a defect: it
    reaches `_claude_code_token`, which on a stale token performs an OAuth
    refresh over the network and rewrites `~/.claude/.credentials.json`. An
    unauthenticated `GET /api/health` must not refresh the operator's
    credentials, so this reads names and file existence only, and the value
    is never read, stored or returned.

    Under-claiming is the safe direction: a run whose credential turns out
    to be invalid fails loudly at run start, whereas a dashboard that
    claimed a model was ready would have the agent half silently absent.
    """
    for name in _credential_env_names():
        if os.environ.get(name):
            return True
    home = Path.home()
    candidates = [
        home / ".claude" / ".credentials.json",
        home / ".local" / "share" / "opencode" / "auth.json",
        Path(os.environ.get("LOCALAPPDATA", "") or "nonexistent")
        / "opencode" / "auth.json",
    ]
    return any(p.exists() for p in candidates)


def health(model_configured: bool) -> dict:
    return {"ok": True, "version": __version__,
            "model_configured": bool(model_configured),
            "tools": _health_tools()}


# ---------------------------------------------------------------------------
# run ids and paths - everything here guards a value that came from a URL


def valid_run_id(run_id: str) -> bool:
    """Syntax gate for a run id taken from the request path.

    The id is used to build a filesystem path, so this is the first of two
    checks; `safe_run_dir` does the containment check. A separator, a dot
    segment, a percent sign, a NUL or a drive letter all fail here, which
    means `safe_run_dir` never has to reason about them.
    """
    rid = str(run_id or "")
    if rid in (".", "..") or not _RUN_ID_RE.fullmatch(rid):
        return False
    return ".." not in rid


def safe_run_dir(root: Path, run_id: str) -> Path | None:
    """The run directory for `run_id`, or None if it is not one.

    Both checks are kept even though either would do alone: the syntax gate
    is what makes the behaviour obvious, and the containment check is what
    holds if the gate is ever widened. `resolve()` follows symlinks, so a
    session directory that is a link out of root is refused here - the id
    came from the URL, and this is the only place that can tell.
    """
    if not valid_run_id(run_id):
        return None
    rootp = Path(root).resolve()
    cand = (rootp / run_id).resolve()
    if cand == rootp or not cand.is_relative_to(rootp):
        return None
    if not cand.is_dir():
        return None
    return cand


def is_session_dir(path: Path) -> bool:
    """A session directory carries meta.json and/or transcript.jsonl - the
    same definition `Session._resume` refuses to run without - plus this
    server's own sidecar for a run that was requested but never executed."""
    return any((path / name).exists() for name in
               ("meta.json", "transcript.jsonl", WEB_STATE_FILE))


# ---------------------------------------------------------------------------
# reading runs off disk


def _blank_run(run_id: str) -> dict:
    return {"id": run_id, "target": "", "mode": "unknown", "state": "failed",
            "started": 0.0, "finished": None, "findings": 0, "note": ""}


def _findings_count(rdir: Path) -> int:
    rows = _read_json(rdir / "findings.json", [])
    return len(rows) if isinstance(rows, list) else 0


def _derive_state(rdir: Path) -> tuple[str, str, float | None]:
    """(state, note, finished) from the artifacts alone.

    For a run this server did not start - one the CLI produced - the files
    are the only evidence. The order matters:

    * no transcript entry at all means nothing was recorded. A run that died
      on its first API call leaves exactly this shape, and calling it `done`
      is how a dead run comes to look clean.
    * a transcript whose last write is NEWER than the last rendered report
      is a pass in progress, and that is checked BEFORE the report. This
      used to be the other way round, which made the live window
      unreachable for any run that had ever rendered a report - i.e. for
      every `argus run --resume`, since the first pass leaves report.* at
      the end. Measured: a transcript appended 0.0s ago beside a 2h-old
      report.md graded ('done', '', <report mtime>) - a run reported
      finished two hours before its own last recorded evidence.
    * a transcript plus a report that covers it is a finished run.
    * a transcript still being appended to with no report at all is
      running, with the measurement in the note. Without this window a live
      CLI run would be labelled failed by a dashboard that merely cannot
      see its process.
    """
    transcript = rdir / "transcript.jsonl"
    if not _has_transcript_entry(transcript):
        return "failed", NOTE_NOTHING_RECORDED, None
    report = rdir / "report.md"
    summary = rdir / "summary.json"
    done_at = max((t for t in (_mtime(report), _mtime(summary))
                   if t is not None), default=None)
    last = _mtime(transcript)
    age = (time.time() - last) if last is not None else None
    # named `fresh`, not `live`: this is a measurement of the file, not a
    # claim about a process, and `live` means the in-memory record elsewhere
    # in this module
    fresh = age is not None and age <= LIVE_TRANSCRIPT_WINDOW_S
    # `>` and not `>=`: a run that renders its report in the same coarse
    # filesystem tick as its last transcript write is finished, and equality
    # must not flip it to running.
    if fresh and (done_at is None or last > done_at):
        if done_at is None:
            note = f"transcript last written {int(age)}s ago; no report yet"
        else:
            note = (f"transcript last written {int(age)}s ago, after the "
                    "last report render; a pass is in progress")
        return "running", note, None
    if done_at is not None:
        return "done", "", done_at
    return "failed", "no report rendered - the run did not finish", None


def run_from_dir(rdir: Path, live: dict | None = None) -> dict:
    """One run row, merged from three sources in increasing authority:
    the artifacts, this server's sidecar, and a live in-memory record - with
    one exception, at the end: neither of the two upper sources may claim
    `done` for a directory that recorded nothing."""
    row = _blank_run(rdir.name)
    meta = _read_json(rdir / "meta.json", {})
    if isinstance(meta, dict):
        row["target"] = str(meta.get("target") or "")
        try:
            row["started"] = float(meta.get("started") or 0.0)
        except (TypeError, ValueError):
            row["started"] = 0.0
    derived = _derive_state(rdir)
    row.update(state=derived[0], note=derived[1], finished=derived[2])

    side = _read_json(rdir / WEB_STATE_FILE, {})
    if isinstance(side, dict) and side:
        for key in ("target", "mode", "note"):
            if isinstance(side.get(key), str) and side[key]:
                row[key] = side[key]
        for key in ("started", "finished"):
            try:
                if side.get(key) is not None:
                    row[key] = float(side[key])
            except (TypeError, ValueError):
                pass
        sstate = side.get("state")
        if sstate in RUN_STATES:
            row["state"] = sstate
            if sstate in ("queued", "running") and live is None:
                # The sidecar is the last thing a dead server wrote. No
                # thread is tracking this run in this process, so reporting
                # it as running would be reporting a thread that does not
                # exist. Fall back to what the artifacts show - reusing the
                # triple derived above rather than deriving it twice - and
                # if they show an unfinished run, say why it is unknown.
                if derived[0] == "done":
                    row.update(state=derived[0], note=derived[1],
                               finished=derived[2])
                else:
                    row.update(state="failed", note=NOTE_STALE, finished=None)
    if live:
        for key in ("target", "mode", "state", "note", "started", "finished"):
            if key in live:
                row[key] = live[key]
    if row["state"] == "done" and derived[1] == NOTE_NOTHING_RECORDED:
        # The one override this file does not allow, and the one its
        # docstring promises it will not: a `done` claimed by the sidecar or
        # by the live record over a directory that recorded nothing. A
        # runner can return normally having recorded nothing (`argus.team.
        # coordinator.run` RETURNS {"lead_error": ...} instead of raising),
        # and the row then read {"state": "done", "note": ""} while
        # `_derive_state` on the same directory said ('failed', 'no
        # transcript entries - nothing was recorded', None) - measured, and
        # permanent after a restart, because a terminal sidecar state skips
        # the stale check above. `blocked` and `failed` are untouched: they
        # claim nothing was run, which is what the artifacts show.
        row.update(state=derived[0], note=derived[1], finished=derived[2])
    # The count comes from the artifact, never from a recorded number: a
    # registry that reports its own tally reports what it intended.
    if (rdir / "findings.json").exists():
        row["findings"] = _findings_count(rdir)
    elif isinstance(side, dict):
        try:
            row["findings"] = int(side.get("findings") or 0)
        except (TypeError, ValueError):
            row["findings"] = 0
    if row["state"] not in RUN_STATES:  # defence in depth; unreachable today
        row["state"] = "failed"
    return row


def scan_runs(root: Path, live: dict[str, dict] | None = None) -> list[dict]:
    """Every session directory under root, newest first.

    Scanned rather than tracked in memory, so a run started by the CLI
    appears in the dashboard too - that is the whole point of pointing both
    at one session directory.
    """
    rootp = Path(root)
    live = live or {}
    out: list[dict] = []
    try:
        entries = sorted(rootp.iterdir())
    except OSError:
        return out
    # Newest first by name - ids are `%Y%m%d-%H%M%S-<host>`, so name order
    # is time order - because the row cap then keeps the newest runs rather
    # than whichever the directory happened to list first.
    for child in reversed(entries):
        if len(out) >= MAX_RUN_ROWS:
            break
        try:
            if not child.is_dir() or not is_session_dir(child):
                continue
        except OSError:
            continue
        # One gate for the list and for the detail route: `safe_run_dir` is
        # what `/api/runs/<id>` and `/api/reports/<id>` resolve through, so
        # a name it refuses has no business in the list - listing a row
        # those two would 404 makes them disagree about what a run is. It
        # refuses an id this tree would not produce and, measured, a session
        # directory that is a SYMLINK out of the root: `child.is_dir()`
        # follows the link, so the row was listed while its own detail and
        # report routes both 404'd through `resolve()`.
        if safe_run_dir(rootp, child.name) is None:
            continue
        out.append(run_from_dir(child, live.get(child.name)))
    out.sort(key=lambda r: (r.get("started") or 0.0, r.get("id") or ""),
             reverse=True)
    return out


def findings_rows(root: Path) -> list[dict]:
    """Findings across every run, flattened for the dashboard table.

    Read through `session.sanitized_findings`, the same view the report
    renderers use: findings.json is operator-editable, and that function is
    what guarantees a hand-edited row cannot take the page down.
    """
    out: list[dict] = []
    for run in scan_runs(root):
        rdir = Path(root) / run["id"]
        if not (rdir / "findings.json").exists():
            continue
        rows = _read_json(rdir / "findings.json", [])
        for f in sanitized_findings(rows if isinstance(rows, list) else []):
            out.append({
                "run_id": run["id"],
                "id": f.get("id", ""),
                "title": f.get("title", ""),
                "severity": f.get("severity", ""),
                "grade": f.get("grade", ""),
                "vuln_class": f.get("vuln_class") or f.get("category", ""),
                "url": f.get("url", ""),
                "excerpt": str(f.get("evidence_excerpt", ""))[:EXCERPT_CAP],
            })
            if len(out) >= MAX_FINDING_ROWS:
                return out
    return out


#: fmt -> (artifact name, content type). `html` is handled separately by the
#: server because it needs more than a content type (see REPORT_FORMATS use
#: in server.py).
REPORT_FORMATS = {
    "md": ("report.md", "text/markdown; charset=utf-8"),
    "html": ("report.html", "text/html; charset=utf-8"),
    "sarif": ("report.sarif", "application/json; charset=utf-8"),
}


def reports_rows(root: Path) -> list[dict]:
    # Bounded by `scan_runs`'s own row cap: this function had no limit of
    # its own, so one directory of thousands of runs was re-stat'd and
    # re-serialised on every dashboard poll.
    out: list[dict] = []
    for run in scan_runs(root):
        rdir = Path(root) / run["id"]
        formats = [fmt for fmt in ("md", "html", "sarif")
                   if (rdir / REPORT_FORMATS[fmt][0]).exists()]
        if not formats:
            continue
        when = max((_mtime(rdir / REPORT_FORMATS[f][0]) or 0.0)
                   for f in formats)
        out.append({"run_id": run["id"], "target": run["target"],
                    "when": when, "findings": run["findings"],
                    "formats": formats})
    return out


def report_path(root: Path, run_id: str, fmt: str) -> Path | None:
    """The artifact for (run, fmt), or None if there is not one.

    Callers must have already rejected a bad id: this goes through
    `safe_run_dir`, so a traversal attempt returns None here too.
    """
    if fmt not in REPORT_FORMATS:
        return None
    rdir = safe_run_dir(root, run_id)
    if rdir is None:
        return None
    path = rdir / REPORT_FORMATS[fmt][0]
    # The filename is a constant, so this cannot escape; resolved and
    # re-checked anyway because the constant is one edit away from not
    # being one.
    real = path.resolve()
    if not real.is_relative_to(Path(root).resolve()) or not real.is_file():
        return None
    return real


# ---------------------------------------------------------------------------
# prompt preview - the gate in front of every run


def _prompts_module():
    """`argus.prompts` if this tree has it, else None.

    The prompt builder and this module are written separately and integrated
    afterwards, so every use of it is optional and every fallback refuses
    rather than admits.
    """
    try:
        from .. import prompts  # type: ignore[attr-defined]
        return prompts
    except Exception:
        return None


def _str_tuple(value, fallback: tuple[str, ...]) -> tuple[str, ...]:
    if isinstance(value, (tuple, list)) and value and \
            all(isinstance(v, str) for v in value):
        return tuple(value)
    return fallback


def modes() -> tuple[str, ...]:
    return _str_tuple(getattr(_prompts_module(), "MODES", None), MODES)


def required_auth_fields() -> tuple[str, ...]:
    return _str_tuple(
        getattr(_prompts_module(), "REQUIRED_AUTH_FIELDS", None),
        REQUIRED_AUTH_FIELDS)


def max_extra_chars() -> int:
    value = getattr(_prompts_module(), "MAX_EXTRA", None)
    return value if isinstance(value, int) and 0 < value <= MAX_EXTRA_CHARS \
        else MAX_EXTRA_CHARS


def _structural_errors(mode: str, target: str, auth: dict | None,
                       extra: str) -> list[str]:
    """Refusals this module applies regardless of what `argus.prompts` says.

    These are additive: they can only refuse a request, never admit one.
    The web server is an entry point that starts scans, so the absence of
    the prompt module, or a change in its shape, must not be able to open
    it. The authorisation requirement for the engagement tier is the one
    that matters - the tier does not open without a note naming who
    authorised it and over what window.
    """
    errors: list[str] = []
    allowed = modes()
    if mode not in allowed:
        errors.append(f"mode must be one of {', '.join(allowed)}")
    target = str(target or "").strip()
    if not target:
        errors.append("target is required")
    elif len(target) > MAX_TARGET_CHARS:
        errors.append(f"target is longer than {MAX_TARGET_CHARS} characters")
    elif any(ch.isspace() for ch in target) or \
            any(ord(ch) < 0x20 or ord(ch) == 0x7f for ch in target):
        # A target carrying whitespace or a control byte would later be split
        # into argv for an external tool, or injected into a log line. Refuse
        # the shape, do not try to clean it.
        errors.append("target must not contain whitespace or control characters")
    else:
        try:
            parsed = urllib.parse.urlsplit(normalise_target(target))
            host = parsed.hostname
            parsed.port     # parsed lazily; this is where `:abc` raises
        except ValueError:
            # Found by a test: `http://[::bad::]/` raised out of the preview,
            # so the dashboard saw a dropped connection instead of a
            # refusal. urlsplit, .hostname and .port each raise on their own
            # malformed input.
            #
            # MEASURED LEAK, which is why the exception text is not echoed:
            # `urlsplit("http://admin:hunter2@ex\u2100ample.com/")` raises
            # from urllib's `_checknetloc` with the ORIGINAL netloc in the
            # message, so interpolating it put the operator's password into
            # this function's return value and from there into the
            # dashboard's HTTP JSON. Any non-ASCII character whose NFKC form
            # contains / ? # @ or : does it (U+2100 normalises to "a/c"), and
            # it fires BEFORE the credential check below, so the ordering of
            # the checks could not save it.
            #
            # Redacting the message was the other option and this is the
            # narrower one: the wording belongs to urllib, it can place the
            # netloc anywhere in the sentence, and a reader of this refusal
            # needs to know their target was rejected - not how a parser in
            # the standard library phrases it.
            errors.append("target is not a usable URL - check the scheme, "
                          "the host and the port")
        else:
            if parsed.scheme not in ("http", "https") or not host:
                errors.append("target must be an http(s) URL with a host")
            elif "@" in parsed.netloc:
                # A credential in the target URL would be written into the
                # prompt and into meta.json, where only declared secret
                # values are redacted. Refused, not masked: there is a
                # header flag for credentials.
                errors.append(
                    "target carries credentials in the URL (user:pass@host) "
                    "- pass them as a header/secret instead, so they are not "
                    "written into the prompt or the session meta")
    if mode == "engagement":
        auth = auth if isinstance(auth, dict) else {}
        for field in required_auth_fields():
            if not str(auth.get(field) or "").strip():
                errors.append(
                    f"engagement mode needs auth.{field}: the intrusive tier "
                    "does not open without an authorisation note")
    cap = max_extra_chars()
    if len(str(extra or "")) > cap:
        errors.append(f"extra is longer than {cap} characters")
    return errors


def normalise_target(target: str) -> str:
    """The target as a URL: the scheme `ScopeGuard` assumes for a bare host.

    Deferred to `argus.prompts` when that module is present, because the
    string stored in the session's meta.json and the string the prompt names
    have to be the same one. Two normalisers agreeing today is not the same
    as one normaliser: `host:8080` is a port to one reading and a scheme to
    the other, and only the module that writes the prompt has the test for
    it.
    """
    mod = _prompts_module()
    fn = getattr(mod, "_normalise_target", None) if mod else None
    if callable(fn):
        try:
            value = fn(target)
            if isinstance(value, str) and value:
                return value
        except Exception:
            pass  # fall through to the local rule
    t = str(target or "").strip()
    if not t:
        return t
    return t if "://" in t else "http://" + t


_FALLBACK_NOTICE = (
    "[argus.web fallback prompt: argus.prompts is not available in this "
    "tree, so this is NOT the mode-specific operating prompt. Treat it as a "
    "placeholder.]")


def _fallback_prompt(mode: str, target: str, auth: dict | None,
                     extra: str) -> str:
    lines = [_FALLBACK_NOTICE, "",
             f"mode: {mode}", f"target: {_redact(normalise_target(target))}"]
    if isinstance(auth, dict) and auth:
        lines.append("authorisation:")
        for field in ("authorised_by", "scope", "window", "reference"):
            value = str(auth.get(field) or "").strip()
            if value:
                lines.append(f"  {field}: {value}")
    if str(extra or "").strip():
        lines += ["", "operator goal:", str(extra).strip()]
    return "\n".join(lines) + "\n"


def _normalise_preview(result) -> tuple[bool, str, list[str]]:
    """Accept the shapes `argus.prompts.preview` might return.

    That module is written separately from this one, so its exact return
    type is not assumed: a mapping, a dataclass, a (ok, prompt, errors)
    tuple and a bare prompt string are all read. Anything unrecognised is a
    refusal, not an admission.
    """
    if result is None:
        return False, "", ["prompt preview returned nothing"]
    if isinstance(result, str):
        return bool(result.strip()), result, []
    if isinstance(result, dict):
        ok = result.get("ok", True)
        prompt = result.get("prompt", "")
        errors = result.get("errors", [])
    elif isinstance(result, (tuple, list)) and len(result) >= 2:
        ok, prompt = result[0], result[1]
        errors = result[2] if len(result) > 2 else []
    elif hasattr(result, "prompt"):
        ok = getattr(result, "ok", True)
        prompt = getattr(result, "prompt", "")
        errors = getattr(result, "errors", [])
    else:
        return False, "", ["prompt preview returned an unreadable result"]
    if isinstance(errors, str):
        errors = [errors]
    elif not isinstance(errors, (list, tuple)):
        errors = []
    return bool(ok), str(prompt or ""), [str(e) for e in errors]


def _call_prompts_preview(mode: str, target: str, auth: dict | None,
                          extra: str, findings_dir: str = ""):
    """Call `argus.prompts.preview` if this tree has it.

    Returns (found, ok, prompt, errors). Several call shapes are tried
    because the caller integrates the two modules afterwards; a TypeError
    from the wrong shape must not look like a validation failure, and a
    missing module must not look like a valid request.
    """
    prompts = _prompts_module()
    preview = getattr(prompts, "preview", None) if prompts else None
    if not callable(preview):
        return (False, False, "", [])
    kw = {"auth": auth, "extra": extra}
    if findings_dir:
        # Only when the caller asked for it: the prompt builder's documented
        # default for an empty value ("use the session's own findings.json
        # and notes.md") is better than a path this module invented.
        kw["findings_dir"] = findings_dir
    attempts = (
        lambda: preview(mode=mode, target=target, **kw),
        lambda: preview(mode, target, auth, extra),
        lambda: preview({"mode": mode, "target": target, "auth": auth,
                         "extra": extra}),
        lambda: preview(mode, target),
    )
    last: TypeError | None = None
    for call in attempts:
        try:
            ok, prompt, errors = _normalise_preview(call())
        except TypeError as exc:
            last = exc
            continue
        except Exception as exc:
            # A raising preview is a refusal with a reason, not a crash of
            # the dashboard.
            return (True, False, "",
                    [f"prompt preview failed: {type(exc).__name__}: "
                     f"{_redact(str(exc))[:200]}"])
        return (True, ok, prompt, errors)
    return (True, False, "",
            [f"prompt preview has an unexpected signature: "
             f"{_redact(str(last))[:200]}"])


def preview_prompt(mode: str, target: str, auth: dict | None = None,
                   extra: str = "", findings_dir: str = "") -> dict:
    """{"ok", "prompt", "errors"} for one console request.

    Fails closed in three ways: structural refusals are added to whatever
    the prompt module says, a non-empty error list forces `ok` false
    whatever it claimed, and a refused request is handed back with an empty
    prompt - a UI that showed a prompt beside a refusal would be handing the
    operator something to paste.
    """
    mode = str(mode or "")
    errors = _structural_errors(mode, target, auth, extra)
    found, ok, prompt, perrors = _call_prompts_preview(
        mode, normalise_target(target), auth, str(extra or ""),
        str(findings_dir or ""))
    for err in perrors:
        if err not in errors:
            errors.append(err)
    if not found:
        ok, prompt = True, _fallback_prompt(mode, target, auth, extra)
    ok = bool(ok) and not errors and bool(str(prompt).strip())
    if not ok:
        prompt = ""
    return {"ok": ok, "prompt": str(prompt), "errors": errors}


# ---------------------------------------------------------------------------
# the run registry


class RunRegistry:
    """Runs this server started: state, event log, and the worker threads.

    The registry owns bookkeeping only. What a run actually *does* is the
    injected `runner`, because the agent/tool orchestration is not this
    module's business and because a web server that reaches straight into
    the agent loop cannot be tested without one. With no runner and no
    model credential the run is `blocked` with a note saying so - it is
    never reported as having run.
    """

    def __init__(self, root: Path, *, model_configured: bool = False,
                 runner: Callable[[dict, Callable[[str], None]], None] | None = None,
                 max_concurrent: int = MAX_CONCURRENT_RUNS,
                 secrets: list[str] | None = None):
        self.root = Path(root)
        self.model_configured = bool(model_configured)
        self.runner = runner
        # The cap this registry was actually built with. The 429 body used
        # to quote the module constant, so a registry built with
        # max_concurrent=1 told the operator "4 runs are already in
        # progress" with one run in flight (measured).
        self.max_concurrent = max(1, int(max_concurrent))
        # Declared credential values, scrubbed out of every string this
        # registry writes or returns. `Session` carries `secret_values`
        # precisely so every artifact writer scrubs them; the event log is a
        # second write path AND a response path, and was wired to neither -
        # measured, a runner logging "Authorization: Bearer sk-live-..."
        # wrote it verbatim into web-run.json and GET /api/runs/<id>
        # returned it. Same >=4 floor as `Session`: a shorter "secret"
        # redacts innocent bytes.
        self._secrets = {s for s in (str(v) for v in (secrets or []))
                         if len(s) >= 4}
        self._lock = threading.Lock()
        self._runs: dict[str, dict] = {}
        self._events: dict[str, list[dict]] = {}
        self._slots = threading.BoundedSemaphore(self.max_concurrent)
        self._threads: list[threading.Thread] = []
        #: runs created since this registry was built, for the lifetime cap
        self._started = 0

    # -- reads ------------------------------------------------------------

    def live(self) -> dict[str, dict]:
        with self._lock:
            return {rid: dict(rec) for rid, rec in self._runs.items()}

    def runs(self) -> list[dict]:
        return scan_runs(self.root, self.live())

    def run(self, run_id: str) -> dict | None:
        rdir = safe_run_dir(self.root, run_id)
        if rdir is None:
            return None
        return run_from_dir(rdir, self.live().get(run_id))

    def events(self, run_id: str) -> list[dict]:
        if not valid_run_id(run_id):
            return []
        with self._lock:
            if run_id in self._events:
                return [dict(e) for e in self._events[run_id]]
        rdir = safe_run_dir(self.root, run_id)
        if rdir is None:
            return []
        side = _read_json(rdir / WEB_STATE_FILE, {})
        rows = side.get("events") if isinstance(side, dict) else None
        out: list[dict] = []
        for row in rows if isinstance(rows, list) else []:
            if not isinstance(row, dict):
                continue
            try:
                ts = float(row.get("ts") or 0.0)
            except (TypeError, ValueError):
                ts = 0.0
            out.append({"ts": ts, "text": str(row.get("text") or "")})
        return out

    # -- writes -----------------------------------------------------------

    def _scrub(self, text) -> str:
        """Every string this registry writes or returns goes through here:
        the `user:pass@` URL mask AND the declared secret values, using
        `Session`'s own redactor so there is one implementation of that
        rule rather than two that drift."""
        return _redact_obj(_redact(text), self._secrets)

    def log(self, run_id: str, text: str) -> None:
        entry = {"ts": round(time.time(), 3),
                 "text": self._scrub(text)[:500]}
        with self._lock:
            if run_id not in self._runs:
                # Not a run this process is tracking: never created here, or
                # evicted after it finished. An event list keyed on an
                # untracked id would grow with nothing to persist it and
                # nothing to read it back.
                return
            events = self._events.setdefault(run_id, [])
            events.append(entry)
            if len(events) > EVENT_CAP:
                del events[:-EVENT_CAP]
        # `_persist` re-checks the record under the lock, so an eviction
        # racing this call drops the write rather than resurrecting a row.
        self._persist(run_id)

    def _evict(self) -> None:
        """Forget the oldest FINISHED runs beyond `MAX_TRACKED_RUNS`.

        Nothing a reader can see is lost: `_persist` has already written the
        state, the note and the event log into <run>/web-run.json, and both
        `run_from_dir` and `events()` fall back to it. An unfinished run is
        never evicted - `live is None` is exactly what tells a reader that
        no thread in this process is tracking a run, so dropping a running
        record would report a live run as stale.
        """
        with self._lock:
            over = len(self._runs) - MAX_TRACKED_RUNS
            if over <= 0:
                return
            oldest = sorted(self._runs.items(),
                            key=lambda kv: (kv[1].get("started") or 0.0,
                                            kv[0]))
            for rid, rec in oldest:
                if over <= 0:
                    break
                if rec.get("state") in ("done", "failed", "blocked"):
                    self._runs.pop(rid, None)
                    self._events.pop(rid, None)
                    over -= 1

    def _set_state(self, run_id: str, state: str, note: str | None = None,
                   finished: float | None = None) -> None:
        assert state in RUN_STATES, state
        with self._lock:
            rec = self._runs.get(run_id)
            if rec is None:
                return
            rec["state"] = state
            if note is not None:
                rec["note"] = str(note)
            if state in ("done", "failed", "blocked"):
                rec["finished"] = finished if finished is not None \
                    else round(time.time(), 3)
            else:
                rec["finished"] = None
        self.log(run_id, f"state: {state}" + (f" - {note}" if note else ""))

    def _persist(self, run_id: str) -> None:
        """Mirror a run's state to <run>/web-run.json.

        So a restarted server still knows the mode, the note and the event
        log of a run it started. Best effort: a failed sidecar write must
        not take down the run or the request that triggered it.
        """
        with self._lock:
            rec = self._runs.get(run_id)
            events = [dict(e) for e in self._events.get(run_id, [])]
            if rec is None:
                return
            payload = dict(rec)
        rdir = self.root / run_id
        payload["events"] = events
        payload["findings"] = _findings_count(rdir)
        payload["prompt_file"] = PROMPT_FILE
        try:
            _atomic_write(rdir / WEB_STATE_FILE,
                          json.dumps(payload, indent=2, ensure_ascii=False))
        except OSError:
            pass

    def create(self, *, mode: str, target: str, auth: dict | None,
               extra: str, prompt: str) -> dict:
        """Create the run directory, write the prompt, start the worker.

        The caller must have validated with `preview_prompt` first; this
        re-checks the scope guard because the guard is the thing that must
        never be bypassed, and `preview_prompt`'s own copy of that check
        lives in `argus.prompts`, which may not be installed.

        Raises ScopeError if the guard refuses the target, TooManyRuns at
        the concurrency cap OR at the lifetime cap, and OSError if the
        directory cannot be written. In every one of those cases nothing has
        been created.
        """
        target = normalise_target(target)
        with self._lock:
            started = self._started
        if started >= MAX_RUNS_PER_SERVER:
            # Checked before the guard and before a slot is taken, so a
            # refused request creates nothing and holds nothing.
            raise TooManyRuns(
                f"this console has started {started} runs since it was "
                f"launched, which is its lifetime cap of "
                f"{MAX_RUNS_PER_SERVER} - restart it, or run from the CLI")
        # A guard built from the target, checked against that target, so be
        # exact about what this does and does not do. MEASURED: `check()` has
        # five raise branches and ONE of them is reachable here - the scheme
        # and parse check, which refuses `ftp://`, `file:///` and anything
        # urlsplit cannot read. The other four cannot fire: the host is the
        # whole allowlist, `exclude_paths` is empty, and `allow_private` is
        # forced True for a private target (scope.py:206), so
        # `http://169.254.169.254/latest/meta-data/`, `http://10.0.0.1/`,
        # `http://192.168.1.1/admin` and `http://[::1]/` all pass with
        # `allow_private=True`. What was written here claimed the opposite -
        # "fail-closed: private addresses are only allowed when the target
        # itself is private" - which is vacuous, since the target is always
        # itself. `prompts.py` carries the same measurement for the same
        # mistake; this is its second site.
        #
        # The real protection on this path is the next line down and it is
        # structural rather than conditional: no `extra_hosts` is accepted
        # over HTTP at all. A scope list arriving in a JSON body would be a
        # scope decision made by whoever reached the port, so there is no
        # parameter for it to arrive in. Scope beyond the target itself comes
        # from the operator's own invocation or not at all.
        guard = ScopeGuard(target)
        guard.check(target)
        if not self._slots.acquire(blocking=False):
            # Refuse before anything is created: a directory written for a
            # run that was never started is a run that looks real.
            raise TooManyRuns(
                f"{self.max_concurrent} run"
                + ("s are" if self.max_concurrent != 1 else " is")
                + " already in progress")
        try:
            meta = {"mode": mode, "goal": str(extra or ""),
                    "started_by": "web",
                    "scope": sorted(guard.allowed_hosts)}
            if isinstance(auth, dict) and auth:
                # The authorisation note belongs in the engagement record:
                # it is the thing that makes the tier legitimate. It is not
                # echoed back by any route.
                meta["authorisation"] = {
                    k: str(auth.get(k) or "")[:500]
                    for k in ("authorised_by", "scope", "window", "reference")}
            # The declared secrets go to the Session too, so its own
            # artifacts (meta.json, notes.md) inherit the same gate as this
            # registry's event log.
            session = Session(self.root, target, meta=meta,
                              secrets=sorted(self._secrets))
            rdir = session.dir
            _atomic_write(rdir / PROMPT_FILE, str(prompt or ""))
            session.note(
                f"Run requested from the web console (mode={mode}). "
                f"Prompt written to {PROMPT_FILE}.")
            # No transcript entry is written here on purpose. The transcript
            # is the evidence chain; seeding it with "someone opened a form"
            # would make a run that probed nothing verify like a real one,
            # and `argus report` / `argus verify` correctly refuse a session
            # whose transcript is empty.
            rec = {"id": rdir.name, "target": self._scrub(target),
                   "mode": mode, "state": "queued",
                   "started": round(session.started, 3),
                   "finished": None, "findings": 0, "note": ""}
            with self._lock:
                self._runs[rdir.name] = rec
                self._events[rdir.name] = []
                self._started += 1
            self._persist(rdir.name)
            info = {"id": rdir.name, "dir": str(rdir), "target": target,
                    "mode": mode, "prompt": str(prompt or ""),
                    "auth": dict(auth) if isinstance(auth, dict) else None,
                    "extra": str(extra or "")}
            thread = threading.Thread(
                target=self._work, args=(info,), daemon=True,
                name=f"argus-web-run-{rdir.name}")
            with self._lock:
                # Dead threads are dropped here rather than accumulated: 60
                # sequential POSTs left 60 Thread objects with 0 alive
                # (measured), because `wait()` iterates a copy and leaves
                # the list intact.
                self._threads = [t for t in self._threads if t.is_alive()]
                self._threads.append(thread)
            thread.start()
        except BaseException:
            self._slots.release()
            raise
        self._evict()
        return dict(rec)

    def _work(self, info: dict) -> None:
        run_id = info["id"]
        try:
            if not self.model_configured:
                self._set_state(run_id, "blocked", NOTE_NO_MODEL)
                return
            if self.runner is None:
                self._set_state(run_id, "blocked", NOTE_NO_RUNNER)
                return
            self._set_state(run_id, "running", "")
            try:
                self.runner(dict(info), lambda text: self.log(run_id, text))
            except Exception as exc:
                self._set_state(
                    run_id, "failed",
                    f"{type(exc).__name__}: {self._scrub(str(exc))[:300]}")
            else:
                # Graded from the artifacts, never from the bare fact that
                # the runner returned. A runner can return normally having
                # recorded nothing - `argus.team.coordinator.run` RETURNS
                # {"lead_error": ...} instead of raising, so a runner built
                # on it returns when the lead agent errored - and this used
                # to record `done` over a directory holding only meta.json,
                # notes.md, prompt.txt and the sidecar (measured).
                if _has_transcript_entry(
                        self.root / run_id / "transcript.jsonl"):
                    self._set_state(run_id, "done", "")
                else:
                    self._set_state(run_id, "failed", NOTE_RUNNER_NO_RECORD)
        finally:
            # A worker that dies on something not caught above - a
            # BaseException, an OOM in the runner - would otherwise leave the
            # run reported as running for as long as the server lives.
            with self._lock:
                stuck = (self._runs.get(run_id) or {}).get("state") \
                    in ("queued", "running")
            if stuck:
                self._set_state(run_id, "failed",
                                "the worker stopped without recording an "
                                "outcome")
            self._persist(run_id)
            self._slots.release()

    def wait(self, timeout: float = 5.0) -> None:
        """Join the worker threads. For tests and for a clean shutdown."""
        deadline = time.time() + timeout
        for thread in list(self._threads):
            thread.join(max(0.0, deadline - time.time()))
