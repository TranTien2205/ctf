"""Hybrid recon/exploit fan-out: external scanners and a model, at once.

The operator insight this module exists for:

    A tool is only as good as the wordlist you already have. An agent can
    GENERATE a wordlist from the patterns it just observed. Running both
    and merging beats either alone.

So a stage here has two halves and they run concurrently:

  * the TOOL half - every selected scanner that is actually installed, one
    subprocess each, all started together, each with its own deadline and
    bounded output.
  * the AGENT half - an injected ``agent_fn(prompt) -> text`` callable that
    reads what the tools have returned SO FAR and proposes more paths,
    parameters and payloads. Its path-shaped suggestions are written to a
    wordlist and ffuf runs AGAIN on that list, which is the insight above
    actually executed rather than described.

The agent is seeded from whatever has landed within a short grace window
(`_AGENT_SEED_GRACE_S`) instead of from the finished tool half, because
waiting for the slowest scanner would make "concurrently" a word rather
than a fact: with one slow tool and a wait-for-all seed there is no overlap
left to exploit.

What this module never does:

  * import an LLM client. `agent_fn` is injected, so the whole module is
    testable with no key, no network and no scanners installed.
  * spawn a process before the caller's ScopeGuard has approved the exact
    target that process will dial.
  * build a command from a string, or pass shell=True. argv is a list
    everywhere; the target is attacker-influenced data.
  * hand a scanner this process's credentials. The child's environment is
    the operator's minus anything whose NAME looks like a credential, the
    same scrub `tools/analysis.run_external` applies - see `_child_env`,
    including what it cannot do without a Session.
  * trust a model suggestion. Everything the agent returns is treated as
    data derived from target bytes - i.e. as potentially chosen by the
    target - and is scope-checked, length-capped, count-capped and refused
    if it could read as a command-line flag.

Scope of the defaults: these are sane default invocations. An operator who
needs a hand-written scanner command still has `tools.analysis.run_external`,
which takes an argument string and applies its own per-tool arg guards. This
module deliberately exposes no "extra args" parameter: a free-text argv tail
would reopen every channel those guards close (local file reads, target
files, --resolve, sqlmap --eval).

Nothing here records to a Session. The caller owns the evidence store, and
a SweepResult carries the argv, the bytes and the timings it needs to
record. A scanner hit is a lead, never a finding: proof grading is
`argus.proof`'s job and these endpoints are candidates for it.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.parse
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from dataclasses import dataclass, field
from pathlib import Path

# How much of each stream is kept. Memory AND disk are bounded: the reader
# threads below keep the first `_MAX_OUTPUT_CHARS` and then go on reading
# and DISCARDING, so a target answering with a gigabyte costs neither this
# process's memory nor a temp file. (`_subproc.run_capped` bounds memory by
# redirecting to a temp file, which is the right trade for the transcript
# and the wrong one here: a gigabyte still lands on disk.)
_MAX_OUTPUT_CHARS = 200_000
_MAX_STDERR_CHARS = 20_000

# A target that answers every path with 200 makes ffuf emit one record per
# wordlist line. Without a cap the fan-out that follows is unbounded.
_MAX_ENDPOINTS = 500
_MAX_ENDPOINT_PARALLEL = 16

# The agent half is a model reading target bytes, so every one of these is
# a bound on what the target can talk the model into asking for.
_MAX_AGENT_SUGGESTIONS = 200
_MAX_AGENT_WORDS = 200
_MAX_AGENT_WORD_LEN = 128
_MAX_AGENT_LINE_LEN = 400
_MAX_PROMPT_EVIDENCE = 20_000
_MAX_PROMPT_PER_RUN = 4_000

# How long to let the tool half run before seeding the agent with what has
# landed. Short on purpose: see the module docstring.
_AGENT_SEED_GRACE_S = 5.0

# Ports nmap looks at in the default recon sweep. A scan parameter, not a
# claim about the target - the scheme still comes from the service nmap
# actually reports (see `_parse_nmap_grepable`).
_WEB_PORTS = "80,443,591,593,832,981,1010,1311,2082,2087,2095,2096,2480," \
             "3000,3001,3128,3333,4243,4567,4711,4712,4993,5000,5104,5108," \
             "5280,5281,5601,5800,6543,7000,7001,7396,7474,8000,8001,8008," \
             "8014,8042,8060,8069,8080,8081,8083,8088,8090,8091,8118,8123," \
             "8172,8181,8222,8243,8280,8281,8333,8443,8500,8834,8880,8888," \
             "8983,9000,9043,9060,9080,9090,9091,9200,9443,9800,9981,12443," \
             "16080,18091,18092,20720,28017"

# The user agent the fetch half announces. Not a disguise: an authorised
# engagement wants its traffic identifiable in the target's own logs.
_UA = "argus-orchestrator (authorised testing)"


@dataclass
class ToolRun:
    """One scanner invocation, or one that was refused before it started.

    `started` is `time.monotonic()`, NOT epoch time, and `seconds` is
    measured on the same clock. That is deliberate: the one question these
    two fields exist to answer is "did these runs overlap", computed as
    [started, started + seconds] per run, and this package has already paid
    for mixing two clocks in one window - `probe_race` reconstructed a
    window from a wall-clock timestamp and a monotonic elapsed_ms, and on
    coarse-clock runners the two disagreed and the gate refused a race the
    probe had announced. One clock, one question. Wall-clock correlation
    belongs to the Session transcript, which timestamps the event the
    caller records for this run.

    `rc` is None when the deadline ended the process: there is no exit
    status in that case, and the partial `stdout` is still parsed, because
    a scanner killed at 180s has usually already emitted its findings.
    """
    tool: str
    argv: list[str]
    rc: int | None
    stdout: str
    stderr: str
    seconds: float
    started: float
    skipped_reason: str = ""


@dataclass
class SweepResult:
    target: str
    tool_runs: list[ToolRun]
    endpoints: list[str]        # merged, de-duplicated, in scope
    agent_ran: bool
    # Why the agent half did not run, when it did not - and it is also set
    # with `agent_ran` True for the one case where the half ran and
    # produced nothing usable, because "no suggestions" and "no model" must
    # not read the same. Empty only when the agent ran and returned usable
    # lines; `agent_ran` is the field that says whether it ran at all.
    agent_note: str
    agent_suggestions: list[str]
    seconds: float


# --------------------------------------------------------------- tool table
#
# The names here must stay a subset of `tools.analysis._ALLOWED_TOOLS`,
# which is the package's one answer to "which binaries may this agent
# start". That invariant is asserted between the two REAL lists in
# `tests/test_orchestrator.py::test_tool_names_are_a_subset_of_the_allowlist`
# rather than by importing the other module here: `tools.analysis` pulls in
# `proof` and `httpclient` (0.9s and httpx), and this module's whole claim
# is that it runs with no network stack involved.
#
# `httpx` is NOT in this table on purpose. The binary called `httpx` on this
# host is the PYTHON httpx CLI (`#!/usr/bin/python3`, a URL fetcher), not
# ProjectDiscovery's prober - it takes no `-json` and emits no JSONL. A
# fan-out that shelled out to "httpx" would silently run the wrong program,
# and it is not in the allowlist either.

_RECON_TOOLS = ("nmap", "ffuf", "nuclei")
_EXPLOIT_TOOLS = ("curl", "nuclei", "sqlmap")
_TOOL_NAMES = tuple(sorted(set(_RECON_TOOLS) | set(_EXPLOIT_TOOLS)))


def available_tools() -> dict:
    """name -> absolute path, for the scanners this host actually has."""
    found: dict[str, str] = {}
    for name in _TOOL_NAMES:
        path = shutil.which(name)
        if not path:
            continue
        if not os.path.isabs(path):
            # `shutil.which` returns what PATH gave it. A relative PATH
            # entry ('' or '.') resolves against the CURRENT directory -
            # and every subprocess here runs with cwd set to the workdir,
            # a directory the scanners themselves write into. Refused
            # rather than passed through `abspath`, which would only
            # freeze in whichever binary that directory happened to hold.
            continue
        found[name] = path
    return found


# ------------------------------------------------------------------ helpers


def _scope_ok(scope, url: str) -> str:
    """"" when the guard allows `url`, else the refusal to report.

    Catches Exception, not ScopeError: a guard is a fail-closed object, so
    an unexpected TypeError out of it has to stop the spawn too. Catching
    only the declared type would turn a bug in the guard into an allow.
    """
    try:
        scope.check(url)
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"
    return ""


def _with_scheme(target: str) -> str:
    return target if "://" in target else "http://" + target


def _userinfo(target: str) -> bool:
    """Does this target carry credentials in the URL?

    It matters because everything in this module becomes argv, and argv is
    world-readable on this host (`/proc/<pid>/cmdline`) and is handed back
    to the caller in `ToolRun.argv`, which is what a report renders. The
    package rule is that a declared credential never reaches an artifact,
    so a sweep over `http://user:pw@host/` is refused rather than quietly
    stripped: stripping would send unauthenticated requests and report them
    as if the credential had been used.
    """
    try:
        p = urllib.parse.urlsplit(_with_scheme(target))
    except ValueError:
        return False
    return bool(p.username or p.password)


def _base_url(target: str) -> str:
    """The directory URL to fuzz under - always ends in '/'."""
    p = urllib.parse.urlsplit(_with_scheme(target))
    path = p.path or "/"
    if not path.endswith("/"):
        path = path.rsplit("/", 1)[0] + "/"
    return urllib.parse.urlunsplit((p.scheme, p.netloc, path, "", ""))


def _host_of(target: str) -> str:
    p = urllib.parse.urlsplit(_with_scheme(target))
    return (p.hostname or "").strip()


_DEFAULT_PORT = {"http": 80, "https": 443}


def _norm_endpoint(url: str) -> str:
    """One spelling per endpoint, so the merge can actually de-duplicate.

    Fragment dropped (never sent), host lower-cased, a default port dropped
    so `http://h:80/x` and `http://h/x` are one endpoint. Query kept: `?id=1`
    and `?id=2` are the same code path but `?id=1` and `?debug=1` are not,
    and dropping the query would throw away the only thing sqlmap can test.

    Dot segments are KEPT, so `/a/../b` and `/b` stay two endpoints. That
    looks like a missed de-duplication and is not one: a difference between
    what a proxy normalises and what the origin resolves is itself a
    finding, so those are two different probes rather than two spellings of
    one. The scope guard collapses them for ITS decision - an exclusion
    cannot be walked past with `..` - which is the place where one spelling
    is the right answer.

    EVERY parse step is inside the guard, and the reason is that the first
    version only guarded `urlsplit`. `ParseResult.port` is a PROPERTY that
    parses on access and raises `ValueError` for a port out of range or one
    that is not a number - after `urlsplit` has already succeeded and after
    `.hostname` has answered. Measured: one ffuf record reading
    `{"url":"http://target.test:99999/x"}` raised
    `ValueError: Port out of range 0-65535` out of `_merge_endpoints`, out
    of `_sweep` and out of `recon_sweep`, losing the whole sweep - every
    other tool's endpoints and the captured bytes with them - on one
    malformed line chosen by the target. A candidate this function cannot
    read is not an endpoint, which is what "" means.
    """
    try:
        p = urllib.parse.urlsplit(url.strip())
        if p.scheme.lower() not in ("http", "https") or not p.hostname:
            return ""
        host = p.hostname.lower().rstrip(".")
        netloc = f"[{host}]" if ":" in host else host
        port = p.port
        if port is not None and port != _DEFAULT_PORT.get(p.scheme.lower()):
            netloc = f"{netloc}:{port}"
        path = p.path or "/"
        return urllib.parse.urlunsplit((p.scheme.lower(), netloc, path,
                                        p.query, ""))
    except Exception:
        # Exception, not ValueError: this reads bytes the target chose, and
        # the cost of one unexpected type here is the entire sweep. Same
        # reasoning as `_scope_ok`, and the same direction - unreadable
        # means refused.
        return ""


def _merge_endpoints(scope, candidates) -> list[str]:
    """Normalise, scope-check, de-duplicate, cap. Order of first sight."""
    out: list[str] = []
    seen: set[str] = set()
    for raw in candidates:
        if not isinstance(raw, str):
            continue
        url = _norm_endpoint(raw)
        if not url or url in seen:
            continue
        seen.add(url)
        if _scope_ok(scope, url):
            continue        # out of scope, or in an excluded path
        out.append(url)
        if len(out) >= _MAX_ENDPOINTS:
            break
    return out


_SLUG_RE = re.compile(r"[^a-z0-9._-]+")


def _slug(text: str, limit: int = 48) -> str:
    """A filesystem-safe stem for an attacker-influenced endpoint.

    An endpoint string decides a directory name below the workdir, so it
    must not be able to contain a separator, a drive letter, '..', or four
    thousand characters. Everything outside [a-z0-9._-] collapses to '-'
    and the result is truncated, which leaves '..' impossible to spell as a
    whole component (it is kept as text, never as a path, and the caller
    prefixes an index so collisions cannot merge two endpoints' output).
    """
    # stripped AFTER truncating: a cut can land on a '.' or '-', and a
    # directory name ending in '.' is not legal on Windows, which this
    # package supports.
    slug = _SLUG_RE.sub("-", text.lower())[:limit].strip("-.")
    return slug or "endpoint"


# ------------------------------------------------------------------ subproc


def _child_env() -> dict:
    """The environment a scanner is given: this one, minus credentials.

    Found by auditing this module, not by a failing test: `_spawn` passed no
    `env`, so every scanner inherited ANTHROPIC_API_KEY and anything else in
    the operator's environment. A scanner binary is a semi-trusted child -
    nuclei executes templates, sqlmap runs its own payload code - and
    `tools/analysis.py` already scrubs exactly this for `run_external`, with
    `tests/test_external.py::test_run_external_env_scrubbed` holding it.
    Reopening the hole in a second spawn path would turn that test into a
    statement about one code path rather than about the package.

    The name pattern is imported, not restated, so there is one definition
    of "this looks like a credential". `argus.mcp` is stdlib-only and costs
    0.06s, and the import is lazy regardless.

    WHAT THIS DOES NOT DO: `run_external` also drops any variable whose
    VALUE equals an operator-declared `--secret`. That needs the Session,
    and this module's public API deliberately takes none - so a caller with
    declared secrets has to scrub those itself. Said out loud, because a
    silent partial scrub is worse than a documented one.
    """
    try:
        from .mcp import MCPClient
        patterns = MCPClient._SECRET_RE
    except Exception:                       # pragma: no cover
        # Fail CLOSED on the common names rather than hand the child
        # everything, if that import ever moves.
        patterns = ("KEY", "TOKEN", "SECRET", "PASSWORD", "CREDENTIAL",
                    "CREDS")
    return {k: v for k, v in os.environ.items()
            if not any(s in k.upper() for s in patterns)}


def _kill_process_tree(proc) -> None:
    """Kill the child AND anything it spawned.

    `tools._subproc._kill_tree` rather than `proc.kill()`, because killing
    the direct child leaves everything it spawned alive, reparented, still
    holding the inherited stdout fd and still talking to the target with no
    ScopeGuard, no rate limit and no place in the transcript. That lesson is
    already paid for in `_subproc.py`, and `tests/test_external.py` plants
    it; re-deriving it here would be a second copy of one fact.

    Imported HERE and not at module scope, and the reason is measured:
    `from .tools._subproc import ...` runs `argus/tools/__init__.py`, which
    imports `registry`, which imports `httpclient` and `proof` - so the
    import alone pulled in httpx, 231KB of proof matrix and 0.9s, and this
    module's claim to need no network stack was simply false. A test
    asserted the claim, the claim was wrong, and this is the fix rather
    than a weaker test. The cost lands on the timeout path, where a scan
    has already overrun by `timeout_s`.
    """
    try:
        from .tools._subproc import _kill_tree
    except Exception:                       # pragma: no cover
        _kill_tree = None                   # type: ignore[assignment]
    if _kill_tree is not None:
        try:
            _kill_tree(proc)
            return
        except Exception:                   # pragma: no cover
            pass
    try:                                    # pragma: no cover
        proc.kill()                         # degraded: one pid, not the tree
    except Exception:
        pass


def _drain(stream, limit: int, sink: list) -> None:
    """Read a pipe to EOF; keep the first `limit` bytes, discard the rest.

    Discarding by reading, not by closing: a scanner whose stdout pipe
    fills blocks in write() and never finishes, so the deadline would fire
    on a tool that had already done its work. Reading and dropping costs
    nothing that has not already been spent.
    """
    kept: list[bytes] = []
    kept_len = 0
    total = 0
    try:
        while True:
            chunk = stream.read(65536)
            if not chunk:
                break
            total += len(chunk)
            if kept_len < limit:
                room = limit - kept_len
                kept.append(chunk[:room])
                kept_len += min(room, len(chunk))
    except Exception:
        pass            # the process died mid-read; keep what we have
    text = b"".join(kept).decode("utf-8", "replace")
    if total > kept_len:
        # Said in the output itself, because a caller reading a parsed
        # endpoint list has no other way to learn the list is partial.
        text += (f"\n[argus] output truncated: kept {kept_len} of "
                 f"{total} bytes")
    sink.append(text)


def _spawn(tool: str, argv: list[str], timeout_s: float,
           cwd: str) -> ToolRun:
    """Run argv with a deadline and bounded output. Never raises.

    A spawn that fails (binary deleted between `which` and here, cwd gone,
    exec denied) is reported as a skipped ToolRun: no process ran, which is
    exactly what `skipped_reason` means. Raising instead would make one
    missing tool lose the whole sweep's other results.
    """
    started = time.monotonic()
    outs: list = []
    errs: list = []
    try:
        # shell=False is the default and is never overridden here. argv is
        # a list, so no part of the target string is ever parsed as syntax.
        extra = {"start_new_session": True} if os.name == "posix" else {}
        proc = subprocess.Popen(
            argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            # stdin from DEVNULL, never inherited: under `argus mcp-serve`
            # this process's stdin IS the host's JSON-RPC channel, and a
            # scanner that reads it (sqlmap prompting, curl with no URL)
            # eats the host's frames and wedges the session with no error
            # anywhere.
            stdin=subprocess.DEVNULL, cwd=cwd, env=_child_env(),
            **extra)
    except Exception as exc:
        return ToolRun(tool=tool, argv=list(argv), rc=None, stdout="",
                       stderr="", seconds=time.monotonic() - started,
                       started=started,
                       skipped_reason=f"spawn failed: "
                                      f"{type(exc).__name__}: {exc}")
    readers = [
        threading.Thread(target=_drain, args=(proc.stdout, _MAX_OUTPUT_CHARS,
                                              outs), daemon=True),
        threading.Thread(target=_drain, args=(proc.stderr, _MAX_STDERR_CHARS,
                                              errs), daemon=True),
    ]
    for r in readers:
        r.start()
    rc: int | None
    timed_out = False
    try:
        rc = proc.wait(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        timed_out = True
        rc = None
        _kill_process_tree(proc)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:       # pragma: no cover
            pass
    for r in readers:
        # Joined with a deadline of its own. The kill signals the whole
        # process group, so EOF normally arrives at once - but a reader that
        # somehow does not finish must not hold the sweep open.
        r.join(timeout=5)
    seconds = time.monotonic() - started
    for pipe in (proc.stdout, proc.stderr):
        try:
            if pipe is not None:
                pipe.close()
        except Exception:                       # pragma: no cover
            pass
    # "the scanner printed nothing" and "we stopped reading" must not look
    # the same. If a reader missed its join, `outs` is empty and the old
    # code reported an empty stdout with no sign that anything was given
    # up on - a clean-looking result for a run nobody finished reading.
    stalled = [r for r in readers if r.is_alive()]
    stdout = outs[0] if outs else ""
    stderr = errs[0] if errs else ""
    if stalled:                                 # pragma: no cover
        stderr = (stderr + f"\n[argus] {len(stalled)} output reader(s) did "
                           "not finish within 5s; the captured output above "
                           "is incomplete")[-_MAX_STDERR_CHARS:]
    if timed_out:
        stderr = (stderr + f"\n[argus] killed after {timeout_s}s; "
                           "partial output above is still parsed"
                  )[-_MAX_STDERR_CHARS:]
    return ToolRun(tool=tool, argv=list(argv), rc=rc, stdout=stdout,
                   stderr=stderr, seconds=seconds, started=started,
                   skipped_reason="")


def _skipped(tool: str, reason: str, argv: list[str] | None = None) -> ToolRun:
    return ToolRun(tool=tool, argv=list(argv or []), rc=None, stdout="",
                   stderr="", seconds=0.0, started=time.monotonic(),
                   skipped_reason=reason)


# ------------------------------------------------------------------ parsers
#
# Every field below was read off this host's real output, not from memory.
# The exact records are quoted where a field name is easy to get wrong.


def _json_lines(text: str):
    """Yield the dict on each JSON line; skip banners and a torn tail.

    The last line of a truncated capture is half a record, and tools print
    non-JSON on stdout (ffuf's banner without -s, nuclei's `-stats` lines).
    Both are skipped rather than guessed at.
    """
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if isinstance(rec, dict):
            yield rec


def _parse_ffuf_jsonl(text: str) -> list[str]:
    """Endpoints out of `ffuf -json` (ffuf 2.1.0-dev), e.g.

        {"input":{"FFUFHASH":"MjJjMjQx","FUZZ":"YWRtaW4="},"position":1,
         "status":301,"length":0,"words":1,"lines":1,"content-type":"",
         "redirectlocation":"/admin/","url":"http://127.0.0.1:18080/admin",
         "duration":2897143,"scraper":{},"resultfile":"","host":"..."}

    `url` is the field to read. `input.FUZZ` is BASE64 under `-json` and
    plain text under `-of json` - measured, both on this host - so
    rebuilding the URL from the input word would produce `/YWRtaW4=` on
    one code path and `/admin` on the other. Hence `-json` plus `url`, and
    no file to read back.
    """
    out: list[str] = []
    for rec in _json_lines(text):
        url = rec.get("url")
        if not isinstance(url, str) or not url:
            continue
        out.append(url)
        loc = rec.get("redirectlocation")
        if isinstance(loc, str) and loc:
            # Relative ('/admin/') or absolute, and an absolute one may
            # point off-host; the merge scope-checks it either way.
            out.append(urllib.parse.urljoin(url, loc))
    return out


def _parse_nuclei_jsonl(text: str) -> list[str]:
    """Endpoints out of `nuclei -jsonl -silent` (nuclei v3.11.0), e.g.

        {"template-id":"fixture-any-200","info":{...},"type":"http",
         "host":"127.0.0.1","port":"18080","scheme":"http",
         "url":"http://127.0.0.1:18080/","path":"/",
         "matched-at":"http://127.0.0.1:18080/robots.txt","ip":"127.0.0.1",
         "timestamp":"...","curl-command":"...","matcher-status":true}

    `matched-at` is the field that names WHERE the match was; `url` is the
    input target and is the same for every record. `template-id` is
    required before a record is read as a finding, because `-stats` puts
    JSON progress lines on the same stream
    ({"duration":"0:00:02","hosts":"1","matched":"0",...}) and those are
    not findings.

    For a non-http template `matched-at` is `host:port` with no scheme;
    `_merge_endpoints` drops it, since a schemeless string is not an
    http(s) endpoint and the scope guard refuses one.
    """
    out: list[str] = []
    for rec in _json_lines(text):
        if not rec.get("template-id"):
            continue
        for key in ("matched-at", "url"):
            val = rec.get(key)
            if isinstance(val, str) and val:
                out.append(val)
                break
    return out


def _parse_nmap_grepable(text: str, host: str) -> list[str]:
    """Endpoints out of `nmap -oG -` (nmap 7.95), e.g.

        Host: 127.0.0.1 (TranTien)\tPorts: 18080/open/tcp//http//SimpleHTTPServer 0.6 (Python 3.14.6)/

    Port fields are port/state/proto/owner/service/rpc/version.

    Two things this does NOT do.

    It does not read the name in parentheses. That is the PTR record, which
    the target's own reverse DNS chooses - using it would let a target put
    a hostname of its choosing into this list. The host scanned is the host
    the caller declared, so that is the host returned.

    It does not guess a scheme from the port number. Measured on this host:
    an unprivileged `-sT` scan of 18080 reports `18080/open/tcp/////` - no
    service token at all - and the same scan with `-sV` reports `http`.
    So the scheme comes from the service nmap actually reported, and a port
    with no service token yields nothing. "8080 is probably http" is an
    invention, and this package does not make those; the recon sweep passes
    `-sV` so the label is observed rather than assumed.
    """
    if not host:
        return []
    out: list[str] = []
    for line in text.splitlines():
        if "Ports:" not in line:
            continue
        # Tab-delimited fields follow the port list on the same line: the
        # real output is `...Ports: 18080/open/tcp//http//SimpleHTTPServer
        # 0.6 (Python 3.14.6)/\tIgnored State: closed (78)`. Cutting at the
        # tab keeps that out of the port split - it happens to survive the
        # field count today, and relying on that would be relying on an
        # `Ignored State` value never containing a comma.
        chunk = line.split("Ports:", 1)[1].split("\t", 1)[0]
        for entry in chunk.split(","):
            fields = entry.strip().split("/")
            if len(fields) < 5:
                continue
            port, state, proto, _owner, service = (f.strip() for f
                                                   in fields[:5])
            if state != "open" or proto != "tcp" or not port.isdigit():
                continue
            svc = service.lower()
            if "https" in svc or "ssl" in svc:
                scheme = "https"
            elif "http" in svc:
                scheme = "http"
            else:
                continue
            netloc = f"[{host}]" if ":" in host else host
            out.append(f"{scheme}://{netloc}:{port}/")
    return out


_PARSERS = {
    "ffuf": lambda run, target: _parse_ffuf_jsonl(run.stdout),
    "nuclei": lambda run, target: _parse_nuclei_jsonl(run.stdout),
    "nmap": lambda run, target: _parse_nmap_grepable(run.stdout,
                                                     _host_of(target)),
    # curl and sqlmap are confirmation tools here, not discovery tools:
    # curl's bytes are the ground truth the caller records, and sqlmap's
    # stdout is prose about one URL. Neither names a new endpoint, and
    # scraping URLs out of free text would invent them.
    "curl": lambda run, target: [],
    "sqlmap": lambda run, target: [],
}


# ------------------------------------------------------------------- argv
#
# One builder per tool. Each returns (argv, url_to_scope_check) or a
# refusal string. The URL returned is the exact one the process will dial,
# so the caller checks THAT, not something near it.


def _bundled_wordlist() -> str:
    path = Path(__file__).resolve().parent / "resources" / "wordlists" / \
        "dirs-small.txt"
    return str(path) if path.is_file() else ""


def _argv_ffuf(binary: str, target: str, workdir: str, wordlist: str,
               timeout_s: int) -> tuple[list[str], str] | str:
    wl = wordlist or _bundled_wordlist()
    if not wl:
        return "no wordlist: pass wordlist= (the bundled list is missing)"
    if not Path(wl).is_file():
        return f"wordlist not found: {wl}"
    # `is_file()` answered in THIS process's cwd; ffuf runs with cwd set to
    # the workdir, so a relative path would be resolved a second time
    # against a different directory. Measured: `workdir='work'` with
    # `wordlist='lists/w.txt'` produced `-w lists/w.txt` and `cwd='work'`,
    # so the child looked for `work/lists/w.txt`, which does not exist -
    # and the "wordlist not found" refusal above, whose whole job is to
    # catch that, had already passed against the real file. ffuf then exits
    # on its own error and the sweep reports a tool run that found nothing.
    # Absolutised here rather than in `_sweep` so BOTH callers get it: the
    # operator's list and the agent's generated one.
    wl = os.path.abspath(wl)
    base = _base_url(target)
    argv = [binary, "-u", base + "FUZZ", "-w", wl,
            # -json: newline-delimited records on stdout, so the bounded
            # capture here is the parser's input and nothing is read back
            # off disk. -s silences the banner. -ic because the bundled
            # lists carry a '#' header line that would otherwise be fuzzed.
            "-json", "-s", "-ic",
            "-t", "20", "-rate", "100", "-timeout", "10",
            # -ac so a target that answers everything with 200 does not
            # produce one "endpoint" per wordlist line.
            "-ac",
            # ffuf's own ceiling, below the subprocess deadline, so the
            # normal end is a clean exit with complete JSONL rather than a
            # kill.
            "-maxtime", str(max(5, int(timeout_s) - 10))]
    return argv, base


def _argv_nuclei(binary: str, target: str, workdir: str, wordlist: str,
                 timeout_s: int, dast: bool = False) -> tuple[list[str], str]:
    url = _with_scheme(target)
    argv = [binary, "-u", url,
            "-jsonl", "-silent", "-nc",
            # -duc: no update check, so an offline or air-gapped run does
            # not spend its deadline on a download.
            "-duc",
            # -ni: no interactsh. OAST would send target-chosen data to a
            # third-party server outside the engagement, and a callback
            # cannot be evidence in an artifact this package can verify.
            "-ni",
            # -or: no raw request/response pairs in the JSON. They would
            # dominate the bounded capture and the caller already records
            # the real bytes through its own client.
            "-or",
            # -dr: never follow a redirect. A template that opts into
            # redirects would otherwise dial whatever Location names, and
            # that host has not been through the scope guard. Same decision
            # as curl's missing -L, for the same reason.
            "-dr",
            "-timeout", "10", "-rl", "100"]
    if dast:
        # The exploit stage runs the fuzzing templates, which is the set
        # that tests a parameter rather than fingerprinting a host.
        #
        # Measured on this host: `-dast` against one endpoint took 12.5s at
        # 378% CPU. `max_parallel` multiplies that, and in a 2-endpoint
        # fan-out both runs hit a 45s deadline through contention alone. It
        # is the expensive half of the exploit stage - a caller with many
        # endpoints should lower max_parallel rather than raise it.
        argv.append("-dast")
    return argv, url


def _nmap_ports(target: str) -> str:
    """The common web ports, plus the one the operator actually named.

    Measured against the loopback fixture on :18080 - a port not in the
    common list - and nmap reported nothing, because the scan never looked
    at the port the target names. A port list that omits the target's own
    port is the one case where this tool cannot fail to be useless.
    """
    try:
        port = urllib.parse.urlsplit(_with_scheme(target)).port
    except ValueError:
        port = None
    if not port:
        return _WEB_PORTS
    if str(port) in _WEB_PORTS.split(","):
        return _WEB_PORTS
    return f"{port}," + _WEB_PORTS


def _argv_nmap(binary: str, target: str, workdir: str, wordlist: str,
               timeout_s: int) -> tuple[list[str], str] | str:
    host = _host_of(target)
    if not host:
        return f"no host in target: {target!r}"
    # nmap takes the host as a BARE POSITIONAL and has no `--`
    # end-of-options marker, so this is the one argv token in the module
    # that a separator cannot protect: it has to be refused here. `_plan`
    # checks the URL this builder returns (`http://<host>`), which can
    # never begin with '-', so the guard that exists for exactly this
    # threat did not cover the one path that needs it.
    #
    # Measured on nmap 7.95 with the token this builder used to produce.
    # For `http://-oG.target.test/`, `urlsplit().hostname` lower-cases to
    # `-og.target.test`, and nmap reads that as `-oG og.target.test`: it
    # wrote its grepable output to a local file `g.target.test` in the
    # workdir, scanned nothing, and exited 0 - so the sweep reported a
    # successful nmap run with no error, no output and no endpoints, which
    # is the "empty, successful-looking recon run" this builder already
    # refuses for IPv6 one case below.
    #
    # Reachable through the real guard, not only in theory:
    # `ScopeGuard.include_subdomains` defaults to True and matches on
    # `host.endswith("." + allowed)`, so `-oG.target.test` is IN SCOPE for
    # the target `target.test`, and a host like that can arrive from a
    # redirect, a nuclei `matched-at`, or a model suggestion.
    bad = _reject_flagish(host)
    if bad:
        return (f"{bad} - nmap takes the host as a bare positional and has "
                f"no '--' end-of-options marker")
    argv = [binary]
    if ":" in host:
        # Measured: `nmap -Pn -sT -p 22 ::1` refuses with ":: 1 looks like
        # an IPv6 target specification -- you have to use the -6 option."
        # and scans nothing, exit 0. An IPv6 engagement would have produced
        # an empty, successful-looking recon run.
        argv.append("-6")
    argv += [
            # -Pn: no host discovery. A host the operator named is in
            # scope whether or not it answers a ping.
            "-Pn",
            # -sT: a connect scan, which needs no privileges. -sS would
            # need root and silently degrade.
            "-sT", "--open",
            # -sV so the service label is OBSERVED - see
            # `_parse_nmap_grepable` for why a port number is not enough.
            "-sV",
            "-p", _nmap_ports(target),
            # nmap's own ceiling under the subprocess deadline.
            "--host-timeout", f"{max(10, int(timeout_s) - 10)}s",
            # -oG -: grepable on stdout. No file, so the bounded capture
            # is the parser's input.
            "-oG", "-",
            host]
    # The URL form is what the scope guard takes; the host is what nmap
    # takes. Same host either way.
    return argv, "http://" + (f"[{host}]" if ":" in host else host)


def _argv_curl(binary: str, target: str, workdir: str, wordlist: str,
               timeout_s: int) -> tuple[list[str], str]:
    url = _with_scheme(target)
    argv = [binary, "-sS", "-i", "-A", _UA,
            "--max-time", str(max(5, min(int(timeout_s), 120))),
            # No -L. Following a redirect means dialling whatever the
            # target names, and that host has not been through the scope
            # guard. The Location header is in the output; the caller can
            # sweep it as an endpoint, where it IS checked.
            # '--' ends options, so a URL that begins with '-' is read as a
            # URL. Belt and braces: `_reject_flagish` already refuses one.
            "--", url]
    return argv, url


def _argv_sqlmap(binary: str, target: str, workdir: str, wordlist: str,
                 timeout_s: int) -> tuple[list[str], str]:
    url = _with_scheme(target)
    has_params = bool(urllib.parse.urlsplit(url).query)
    argv = [binary, "-u", url,
            "--batch", "--disable-coloring",
            # Detection only. --technique excludes S (stacked queries,
            # which executes a second statement - a write channel) and Q
            # (inline queries), leaving boolean, error, UNION and
            # time-based. This package proves injection by reading data the
            # query returns, and stops there: no --dump, no --os-shell, no
            # --file-write, no --tamper.
            "--technique=BEUT",
            "--level=1", "--risk=1",
            # --ignore-redirects, and this one was measured rather than
            # reasoned about: against the loopback fixture sqlmap asked
            # "got a 301 redirect to '...'. Do you want to follow? [Y/n]"
            # and --batch answered Y, so it dialled a URL the scope guard
            # had never seen. A redirect target is chosen by the target. It
            # is in the output, and the caller can sweep it as an endpoint,
            # where it IS checked.
            "--ignore-redirects",
            "--timeout=10", "--retries=1", "--threads=2",
            # Session state under the caller's workdir, not under
            # ~/.local/share/sqlmap. Two endpoints on one host otherwise
            # share sqlmap's per-host session directory, and concurrent runs
            # corrupt each other's session file; --flush-session also stops a
            # stale earlier verdict being reported as this run's.
            f"--output-dir={workdir}", "--flush-session"]
    if not has_params:
        # Without a parameter sqlmap has nothing to test and exits having
        # said so. --forms makes it parse the page's forms, which is the
        # only way a bare path is testable at all.
        argv.append("--forms")
    return argv, url


_BUILDERS = {
    "ffuf": _argv_ffuf,
    "nuclei": _argv_nuclei,
    "nmap": _argv_nmap,
    "curl": _argv_curl,
    "sqlmap": _argv_sqlmap,
}


def _reject_flagish(value: str) -> str:
    """A token that could be read as a flag never reaches argv.

    `ffuf -u`, `nuclei -u` and `sqlmap -u` are Go/optparse flag parsers:
    a VALUE beginning with '-' is taken as the next option, so an endpoint
    spelled `-oOUT` would turn a scan into a file write. Endpoints reach
    here from scanner output and from the model, i.e. from bytes the target
    chose, so this is checked rather than assumed. `_norm_endpoint` already
    requires a scheme, which makes it unreachable for a normalised URL;
    kept because the two guards are one line apart in different functions
    and only this one states the reason.
    """
    if value.startswith("-"):
        return f"refusing a target that reads as a flag: {value!r}"
    if any(c in value for c in "\r\n\x00"):
        return "refusing a target containing a control character"
    return ""


# ------------------------------------------------------------------- agent


def _agent_prompt(subject: str, context: str, stage: str,
                  runs: list[ToolRun], pending: list[str]) -> str:
    """The prompt for the agent half. Bounded, and honest about partials.

    `subject` is what THIS sweep covers and `context` the engagement
    target. They differ in a fan-out, and naming only the engagement target
    - which is what the first version did - asked the model to extend
    evidence collected from /admin while telling it the subject was /.
    """
    lines = [
        f"You are the agent half of a hybrid {stage} stage against "
        f"{subject}.",
        "",]
    if context and context != subject:
        lines += [f"The engagement target is {context}; this stage covers "
                  f"{subject}.", ""]
    lines += [
        "The tool half is running right now. Below is what it has returned",
        "SO FAR - it may be partial, and tools still running are listed as",
        "pending. Read the real output and extend it.",
        "",
    ]
    if pending:
        lines.append("pending tools: " + ", ".join(sorted(set(pending))))
    budget = _MAX_PROMPT_EVIDENCE
    for run in runs:
        if budget <= 0:
            break
        if run.skipped_reason:
            block = f"$ {run.tool}: not run ({run.skipped_reason})"
        else:
            excerpt = run.stdout[:_MAX_PROMPT_PER_RUN] or "(no output)"
            block = (f"$ {' '.join(run.argv)}\n"
                     f"rc={run.rc} seconds={run.seconds:.1f}\n{excerpt}")
        block = block[:budget]
        budget -= len(block)
        lines += ["", block]
    lines += [
        "",
        "Propose what to try next, derived from the patterns ABOVE - a",
        f"naming convention, an extension, a parameter name, a version. At "
        f"most {_MAX_AGENT_SUGGESTIONS} items.",
        "",
        "Format: ONE item per line. No prose, no numbering, no code fences.",
        "A path starts with '/' (e.g. /api/v2/users). A bare word is a",
        "wordlist entry (e.g. admin-backup). A parameter is name=value.",
        "",
        "Rules: the target host only - a suggestion naming another host is",
        "discarded. Nothing destructive: no deletes, no shutdowns, no",
        "password resets, no mass requests. Do not invent a version or a",
        "CVE that is not in the output above.",
    ]
    return "\n".join(lines)


_BULLET_RE = re.compile(r"^(?:[-*+]|\d+[.)])\s+")


def _parse_suggestions(text: str) -> list[str]:
    """One suggestion per line, with the model's formatting habits removed.

    Deliberately not a JSON contract: a model that answers with prose
    should degrade to "a few usable lines", not to an exception.
    """
    out: list[str] = []
    seen: set[str] = set()
    for raw in str(text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("```") or line.startswith("#"):
            continue
        line = _BULLET_RE.sub("", line).strip().strip("`").strip()
        if not line or len(line) > _MAX_AGENT_LINE_LEN:
            continue        # a long line is prose, not a path
        if not line.isprintable():
            continue        # control characters: never, in anything
        if line in seen:
            continue
        seen.add(line)
        out.append(line)
        if len(out) >= _MAX_AGENT_SUGGESTIONS:
            break
    return out


def _suggestion_endpoints(base: str, suggestions: list[str]) -> list[str]:
    """Suggestions that name a location, resolved against the base URL.

    Not scope-checked here: `_merge_endpoints` is the one place that
    decides, so there is a single gate rather than two that can drift.

    `urljoin` is inside the guard because it PARSES its second argument:
    measured, a suggestion of `//[::1` raises `ValueError: Invalid IPv6
    URL` and that raise came out of `recon_sweep`, so a model talked into
    emitting one line lost the whole stage's tool results. One suggestion
    this function cannot resolve is one suggestion dropped.
    """
    out: list[str] = []
    for s in suggestions:
        try:
            if s.startswith(("http://", "https://")):
                out.append(s)
            elif s.startswith("//"):
                # Protocol-relative: by URL semantics this names ANOTHER
                # host, so it is resolved as written and left for the guard
                # to refuse. A first version stripped the slashes, which
                # turned '//evil.test/x' into a path on the in-scope host -
                # an endpoint nobody proposed, named after a directory that
                # does not exist, with the refusal hidden. Rewriting a
                # suggestion into a different one is inventing it.
                out.append(urllib.parse.urljoin(base, s))
            elif s.startswith("/"):
                # Read as written: a leading slash means root-absolute, so
                # it is NOT re-based under the target's directory. The
                # guard's host rules and the operator's path exclusions
                # decide whether that is allowed; guessing "they probably
                # meant inside /app/" would be this module inventing a
                # second scope policy.
                out.append(urllib.parse.urljoin(base, s))
            elif "=" in s and " " not in s and not s.startswith("="):
                # name=value: a parameter on the base URL, which is the only
                # thing sqlmap can test.
                out.append(base + "?" + s)
        except Exception:
            continue
    return out


def _agent_words(scope, base: str, suggestions: list[str]) -> list[str]:
    """The agent's wordlist - the point of the whole module.

    Every word is scope-checked AS THE URL FFUF WOULD REQUEST IT, before
    the file is written. ffuf substitutes the word into the FUZZ position
    itself, so a word like `../../../etc/passwd`, or one that lands inside
    an operator `--exclude` path, would otherwise be sent with no guard
    ever seeing it: this is the only place that can refuse it.

    The asymmetry with the operator's own `wordlist=` is deliberate and
    worth stating: that file is operator-declared input at the same trust
    level as the scope flags themselves, and it is passed to ffuf as given.
    This list is written by a model that just read the target's bytes, so
    the target has a say in it.
    """
    out: list[str] = []
    for s in suggestions:
        word = s.strip().lstrip("/")
        if not word or len(word) > _MAX_AGENT_WORD_LEN:
            continue
        if any(c in word for c in " \t\r\n\x00") or not word.isprintable():
            continue        # ffuf fuzzes one token; whitespace means prose
        if word.startswith("-"):
            continue        # never let a model-written token read as a flag
        try:
            asked = urllib.parse.urljoin(base, word)
        except Exception:
            # `urljoin` parses the word: `//[::1` raises ValueError, and an
            # uncaught raise here loses the stage. A word whose request URL
            # cannot even be built is a word the guard cannot be asked
            # about, so it is refused - the same direction as every other
            # line in this loop.
            continue
        if _scope_ok(scope, asked):
            continue
        if word in out:
            continue
        out.append(word)
        if len(out) >= _MAX_AGENT_WORDS:
            break
    return out


@dataclass
class _AgentHalf:
    ran: bool = False
    note: str = ""
    suggestions: list[str] = field(default_factory=list)


def _call_agent(agent_fn, prompt: str) -> _AgentHalf:
    """The agent half, as it runs on its own thread. Never raises."""
    try:
        reply = agent_fn(prompt)
    except Exception as exc:
        # The model path is the one that fails for reasons outside this
        # process - no key, rate limit, a 529. That is a note, not a
        # traceback that loses the tool half's results.
        return _AgentHalf(False, f"agent_fn raised "
                                 f"{type(exc).__name__}: {exc}")
    if not isinstance(reply, str) or not reply.strip():
        return _AgentHalf(False, "agent_fn returned no text")
    sugg = _parse_suggestions(reply)
    if not sugg:
        return _AgentHalf(True, "agent returned no usable lines", [])
    return _AgentHalf(True, "", sugg)


# -------------------------------------------------------------------- stage


def _plan(names, stage: str, target: str, workdir: str, wordlist: str,
          timeout_s: int, scope, installed: dict) -> list:
    """Decide, for each selected tool, argv or the reason there is none.

    Everything that can refuse a run happens here, before any process
    exists: unknown name, not installed, no wordlist, out of scope.
    """
    planned: list = []
    for name in names:
        if name not in _BUILDERS:
            # Named, not silently dropped: an operator who typo'd a tool
            # name must not read the result as "that scanner found nothing".
            planned.append((name, None, _skipped(
                name, f"unknown tool {name!r}; known: "
                      f"{sorted(_BUILDERS)}")))
            continue
        binary = installed.get(name)
        if not binary:
            planned.append((name, None, _skipped(
                name, f"{name} is not installed on this host")))
            continue
        builder = _BUILDERS[name]
        kwargs = {}
        if name == "nuclei" and stage == "exploit":
            kwargs["dast"] = True
        built = builder(binary, target, workdir, wordlist, timeout_s,
                        **kwargs)
        if isinstance(built, str):
            planned.append((name, None, _skipped(name, built)))
            continue
        argv, dial = built
        bad = _reject_flagish(dial)
        if bad:
            planned.append((name, None, _skipped(name, bad, argv)))
            continue
        refusal = _scope_ok(scope, dial)
        if refusal:
            # The argv is kept so the caller can see what WOULD have run,
            # and `skipped_reason` records that nothing did.
            planned.append((name, None, _skipped(
                name, f"out of scope: {refusal}", argv)))
            continue
        planned.append((name, (argv, dial), None))
    return planned


def _sweep(target: str, *, scope, workdir, names, agent_fn, timeout_s: int,
           wordlist: str, stage: str, context: str = "") -> SweepResult:
    """One stage: the tool half and the agent half, concurrently, merged."""
    t0 = time.monotonic()
    target = str(target or "").strip()
    timeout_s = max(5, int(timeout_s or 5))
    # De-duplicated: `slots` and the future map are keyed by tool name, so
    # tools=["ffuf", "ffuf"] silently collapsed two requested runs into one
    # result and the caller could not tell which.
    names = list(dict.fromkeys(names))

    def refuse_all(reason: str, note: str) -> SweepResult:
        return SweepResult(
            target=target,
            tool_runs=[_skipped(n, reason) for n in names],
            endpoints=[], agent_ran=False, agent_note=note,
            agent_suggestions=[], seconds=time.monotonic() - t0)

    if not target:
        return refuse_all("no target given", "no target given")

    bad = _reject_flagish(target)
    if bad:
        return refuse_all(bad, bad)

    if _userinfo(target):
        # See `_userinfo`: argv is world-readable and is handed back to the
        # caller for its report, so a credential in the URL cannot be
        # passed to a scanner here. Refused rather than stripped, because a
        # stripped run reports unauthenticated results as authenticated ones.
        reason = ("target carries credentials in the URL; argv is "
                  "world-readable and is returned to the caller, so this "
                  "sweep is refused rather than leaking or silently "
                  "dropping them")
        return refuse_all(reason, reason)

    refusal = _scope_ok(scope, _with_scheme(target))
    if refusal:
        # The whole point of the pre-check: a refused target produces
        # skipped ToolRuns and NO process, and the agent does not run
        # either - there is nothing it would be allowed to act on.
        reason = f"target refused by scope guard: {refusal}"
        return refuse_all(reason, reason)

    # Absolute, because every child runs with `cwd` set to this directory:
    # a relative workdir is resolved against the parent's cwd here and
    # against the workdir itself inside the child, so `--output-dir=<wd>`
    # and the agent's `mkstemp` wordlist would both name a path the child
    # cannot see. `abspath`, not `resolve`: it touches no filesystem and
    # does not rewrite a symlinked directory the operator named.
    wd = Path(os.path.abspath(workdir))
    try:
        wd.mkdir(parents=True, exist_ok=True)
    except Exception as exc:
        reason = f"workdir unusable: {type(exc).__name__}: {exc}"
        return refuse_all(reason, reason)

    base = _base_url(target)
    installed = available_tools()
    planned = _plan(names, stage, target, str(wd), wordlist, timeout_s,
                    scope, installed)

    agent = _AgentHalf()
    agent_endpoints: list[str] = []
    runnable = [(n, p) for n, p, _s in planned if p]
    # Order preserved for the caller: one entry per selected tool, in the
    # order the tools were selected, with the agent's extra ffuf appended.
    slots: dict[str, ToolRun] = {}
    for name, plan, skipped in planned:
        if skipped is not None:
            slots[name] = skipped

    # Threads: one per runnable tool plus two readers each, plus one for the
    # agent. Bounded by the tool table (3 per stage) and, in a fan-out, by
    # max_parallel.
    pool = ThreadPoolExecutor(max_workers=max(1, len(runnable)) + 1,
                              thread_name_prefix="argus-tool")
    try:
        futs: dict[Future, str] = {}
        for name, (argv, _dial) in runnable:
            futs[pool.submit(_spawn, name, argv, timeout_s, str(wd))] = name

        if agent_fn is None:
            agent.note = ("no agent_fn given (no model configured); the "
                          "tool half ran on its own")
        elif not callable(agent_fn):
            agent.note = f"agent_fn is not callable: {type(agent_fn).__name__}"
        else:
            # Seed from what has landed inside the grace window, then run
            # the agent CONCURRENTLY with whatever is still going. Waiting
            # for the tool half to finish would serialise the two halves,
            # and with one slow tool there would be no overlap at all.
            if futs:
                wait(list(futs), timeout=_AGENT_SEED_GRACE_S,
                     return_when=FIRST_COMPLETED)
            seed: list[ToolRun] = []
            pending: list[str] = []
            for fut, name in futs.items():
                if fut.done():
                    try:
                        seed.append(fut.result())
                    except Exception as exc:        # pragma: no cover
                        seed.append(_skipped(name, f"run failed: {exc}"))
                else:
                    pending.append(name)
            seed += [s for s in slots.values()]
            prompt = _agent_prompt(target, context, stage, seed,
                                   pending)
            # A Python thread cannot be cancelled, so a hung agent_fn is
            # bounded by abandoning it, not by killing it. For that word to
            # be true the thread has to be a DAEMON thread, and a
            # ThreadPoolExecutor worker is not one: `concurrent.futures`
            # registers `_python_exit` with `threading._register_atexit`,
            # which JOINS every pool worker at interpreter shutdown.
            # Measured with the pool this replaced - agent_fn sleeping,
            # timeout_s=5: the sweep returned after 5.0s with
            # `agent_ran=False` and the note below, and then the process
            # could not exit at all. It was still alive when the harness
            # killed it at 25s. The sweep came back and the engagement
            # still hung, which is the exact failure this code says it
            # prevents.
            #
            # A plain daemon thread is not joined at exit, so "abandoned"
            # means abandoned. The real fix still belongs to the LLM
            # client's own HTTP timeout; this is the fallback.
            box: list[_AgentHalf] = []
            done = threading.Event()

            def run_agent() -> None:
                try:
                    box.append(_call_agent(agent_fn, prompt))
                except BaseException as exc:
                    # `_call_agent` catches Exception; this is everything
                    # else - a SystemExit out of a client library, a
                    # BaseException-derived timeout. Named rather than left
                    # to the fallback note below, which says "did not
                    # return within Ns", and for a call that DID return -
                    # by raising - that sentence is simply false. It also
                    # keeps the raise off the interpreter's unhandled-
                    # thread-exception path, where it would print a
                    # traceback nothing in the result refers to.
                    box.append(_AgentHalf(
                        False, f"agent_fn raised {type(exc).__name__}: {exc}"))
                finally:
                    done.set()

            agent_thread = threading.Thread(target=run_agent,
                                            name="argus-agent", daemon=True)
            agent_thread.start()
            # What is LEFT of the stage, not another full timeout_s: the
            # agent has been running since the grace window, and granting it
            # a second full budget made a sweep take twice its own deadline.
            remaining = max(5.0, timeout_s - (time.monotonic() - t0))
            done.wait(timeout=remaining)
            # `box`, not `done.is_set()`: the append happens before the
            # set, so a populated box is the only thing that proves a
            # result exists. Reading it out of a box rather than out of a
            # Future is also what keeps a raise inside the agent half - a
            # future's `.result()` re-raises whatever `_call_agent` did not
            # catch, straight through `_sweep`, losing the tool half's
            # results for a failure the agent half exists to absorb.
            if box:
                agent = box[0]
            else:
                agent.note = (f"agent_fn did not return within "
                              f"{remaining:.0f}s of stage budget; "
                              "abandoned (a thread cannot be cancelled - "
                              "bound the call in the client)")

        if agent.ran and agent.suggestions:
            agent_endpoints = _suggestion_endpoints(base, agent.suggestions)
            # THE INSIGHT, EXECUTED: the agent's words become a wordlist and
            # ffuf runs again on it, merged with the first pass. Submitted to
            # the same pool, so it overlaps any tool still running.
            words = _agent_words(scope, base, agent.suggestions)
            # `tools=` is the operator's answer to which scanners may run,
            # and it binds this pass too. It did not: `installed` is what
            # the HOST has, so `recon_sweep(tools=["nuclei"])` with an
            # agent spawned an ffuf process the operator had excluded -
            # measured, `['nuclei', 'ffuf']` for a one-tool selection. In
            # scope and rate-limited, but not asked for, and an engagement
            # that forbids directory brute-forcing forbids it here as well.
            ffuf_bin = installed.get("ffuf") if "ffuf" in names else None
            if words and ffuf_bin and stage == "recon":
                try:
                    fd, path = tempfile.mkstemp(prefix="agent-words-",
                                                suffix=".txt", dir=str(wd))
                    # mkstemp, not a fixed name: two sweeps sharing a
                    # workdir would otherwise overwrite each other's list
                    # mid-scan.
                    with os.fdopen(fd, "w", encoding="utf-8") as fh:
                        fh.write("\n".join(words) + "\n")
                except Exception as exc:
                    slots["ffuf-agent"] = _skipped(
                        "ffuf-agent", f"could not write the agent wordlist: "
                                      f"{type(exc).__name__}: {exc}")
                else:
                    built = _argv_ffuf(ffuf_bin, target, str(wd), path,
                                       timeout_s)
                    if isinstance(built, str):      # pragma: no cover
                        slots["ffuf-agent"] = _skipped("ffuf-agent", built)
                    else:
                        argv, dial = built
                        refusal = _scope_ok(scope, dial)
                        if refusal:                 # pragma: no cover
                            slots["ffuf-agent"] = _skipped(
                                "ffuf-agent", f"out of scope: {refusal}",
                                argv)
                        else:
                            futs[pool.submit(_spawn, "ffuf-agent", argv,
                                             timeout_s, str(wd))] = \
                                "ffuf-agent"
            elif words and stage == "recon":
                # Named, not dropped - the same rule `_plan` follows for a
                # tool that is not installed. The module's whole thesis is
                # that these words become a second pass; when they cannot,
                # `tool_runs` has to say so, or a caller reads "the agent
                # suggested 40 paths" and has no way to learn that none of
                # them was ever requested.
                why = ("ffuf is not installed on this host"
                       if "ffuf" in names else
                       "ffuf was not in tools=, so the agent's wordlist "
                       "was not run")
                slots["ffuf-agent"] = _skipped(
                    "ffuf-agent", f"{len(words)} agent word(s) generated "
                                  f"but not fuzzed: {why}")

        for fut, name in futs.items():
            try:
                slots[name] = fut.result()
            except Exception as exc:                # pragma: no cover
                slots[name] = _skipped(name, f"run failed: "
                                             f"{type(exc).__name__}: {exc}")
    finally:
        # The tool pool IS joined: its work is bounded by `timeout_s` and
        # the kill path, so waiting is both cheap and necessary - a reader
        # thread still holding a pipe is a resource, not garbage. The agent
        # thread is deliberately not joined; see the daemon note above.
        pool.shutdown(wait=True)

    ordered: list[ToolRun] = []
    for name in names:
        if name in slots:
            ordered.append(slots.pop(name))
    for name in list(slots):
        ordered.append(slots.pop(name))

    candidates: list[str] = [_with_scheme(target)]
    for run in ordered:
        if run.skipped_reason:
            continue
        parser = _PARSERS.get(run.tool) or _PARSERS.get(
            run.tool.split("-", 1)[0])
        if parser is None:
            continue
        try:
            candidates += parser(run, target)
        except Exception:               # pragma: no cover
            # A parser is reading target-chosen bytes. One malformed record
            # must not lose the other tools' endpoints.
            continue
    candidates += agent_endpoints

    return SweepResult(
        target=target,
        tool_runs=ordered,
        endpoints=_merge_endpoints(scope, candidates),
        agent_ran=agent.ran,
        agent_note=agent.note,
        agent_suggestions=list(agent.suggestions),
        seconds=time.monotonic() - t0,
    )


# ------------------------------------------------------------------- public


def recon_sweep(target, *, scope, workdir, tools=None, agent_fn=None,
                timeout_s=180, wordlist="") -> SweepResult:
    """Recon stage: nmap + ffuf + nuclei, and the agent, concurrently.

    `tools` restricts the tool half to the named tools (an iterable of
    names; a mapping like `available_tools()` works, since iterating it
    yields the names). An unknown name is reported as a skipped ToolRun
    rather than dropped. It binds the AGENT half's extra ffuf run too: a
    selection without `ffuf` gets no `ffuf-agent` run, and `tool_runs`
    says the words were generated and not fuzzed rather than leaving the
    caller to notice.

    `wordlist` is the operator's own list for ffuf; the bundled
    `resources/wordlists/dirs-small.txt` is used when it is empty. The
    agent's generated list is a SEPARATE ffuf run (`ffuf-agent`), so the
    operator's list and the model's are both visible in `tool_runs`.

    nuclei runs its OWN default template selection - 13,900 templates on
    this host, by its own count - and it does not finish inside a typical
    deadline. Measured against a static loopback fixture, which is about
    the least work a target can give it: at `timeout_s=60` it was killed
    with 0 bytes of output, and at `timeout_s=180` it was killed with
    12,971 bytes already emitted.

    That is why the deadline path parses rather than discards: the
    subprocess is killed at `timeout_s`, `rc` is None, and whatever JSONL
    it had already written is merged. A caller who wants nuclei to finish
    wants a narrower template set, which is a hand-written invocation -
    `tools.analysis.run_external` - or a much longer `timeout_s`.
    """
    names = list(tools) if tools is not None else list(_RECON_TOOLS)
    return _sweep(target, scope=scope, workdir=workdir, names=names,
                  agent_fn=agent_fn, timeout_s=timeout_s, wordlist=wordlist,
                  stage="recon")


def exploit_fanout(target, endpoints, *, scope, workdir, agent_fn=None,
                   timeout_s=180, max_parallel=4) -> list[SweepResult]:
    """One SweepResult per endpoint, all endpoints worked concurrently.

    `target` is the engagement target. It is CONTEXT - it names the
    engagement in the agent prompt - and it is not itself dialled, so it is
    not what the guard is asked about: every ENDPOINT is scope-checked
    inside its own sweep, before any process exists. (This docstring used to
    claim an up-front check on `target` that the code does not make, which
    is the kind of sentence that gets believed.) Each result's own `target`
    field is the endpoint that result covers.

    Every endpoint gets its own directory under `workdir`. That is not
    tidiness: sqlmap keys its session files by target host, so two
    endpoints on one host would share a session directory and two
    concurrent runs would corrupt each other's state.
    """
    eps: list[str] = []
    seen: set[str] = set()
    for raw in endpoints or []:
        ep = str(raw or "").strip()
        if not ep or ep in seen:
            continue
        seen.add(ep)
        eps.append(ep)
        if len(eps) >= _MAX_ENDPOINTS:
            break
    if not eps:
        return []

    # max(1, ...): a caller passing 0 or a negative would otherwise make
    # ThreadPoolExecutor raise ValueError, turning a degenerate argument
    # into a crash. Capped so a 500-endpoint list cannot ask for 500
    # concurrent scanner processes.
    workers = max(1, min(int(max_parallel or 1), _MAX_ENDPOINT_PARALLEL))
    wd = Path(workdir)
    out: list[SweepResult] = []
    with ThreadPoolExecutor(max_workers=workers,
                            thread_name_prefix="argus-endpoint") as pool:
        futs = []
        for i, ep in enumerate(eps):
            sub = wd / f"ep-{i:03d}-{_slug(ep)}"
            futs.append(pool.submit(
                _sweep, ep, scope=scope, workdir=sub,
                names=list(_EXPLOIT_TOOLS), agent_fn=agent_fn,
                timeout_s=timeout_s, wordlist="", stage="exploit",
                context=str(target or ep)))
        for fut, ep in zip(futs, eps):
            try:
                out.append(fut.result())
            except Exception as exc:        # pragma: no cover
                # `_sweep` is written not to raise; if it ever does, the
                # other endpoints' results still come back.
                out.append(SweepResult(
                    target=ep, tool_runs=[], endpoints=[], agent_ran=False,
                    agent_note=f"sweep failed: {type(exc).__name__}: {exc}",
                    agent_suggestions=[], seconds=0.0))
    return out
