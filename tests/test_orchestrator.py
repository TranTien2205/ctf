"""orchestrator: the hybrid fan-out, offline.

Every test here runs with NO scanner installed, NO network and NO model:
`shutil.which` and `subprocess.Popen` are faked, and the scope guard is a
duck-typed object that records what it was asked. That is not only for
speed - the module's claim is that it never imports an LLM client and never
dials anything the guard has not approved, and a test that needed a key or
a socket could not check either claim.

Both directions throughout. The refusals are the half that matters: an
out-of-scope target that still spawns a process, or a model suggestion that
reaches argv, is the failure this module exists to prevent.
"""
from __future__ import annotations

import io
import os
import subprocess
import sys
import threading
import time
import urllib.parse
from pathlib import Path

import argus.orchestrator as orch
from argus.orchestrator import (SweepResult, ToolRun, available_tools,
                                exploit_fanout, recon_sweep)

REPO = Path(__file__).resolve().parent.parent


# ----------------------------------------------------------------- doubles


class FakeScope:
    """The only surface the orchestrator may use: `.check(url)`.

    Deliberately not a ScopeGuard subclass. If the module ever reaches for
    another attribute - `allowed_hosts`, `allow_private`, an internal cache -
    these tests break, which is the point: the guard is handed in, and a
    module that reads its internals has stopped asking it.
    """

    def __init__(self, hosts=("target.test",), exclude=()):
        self.hosts = {h.lower() for h in hosts}
        self.exclude = [e.rstrip("/") for e in exclude]
        self.checked: list[str] = []

    def check(self, url: str):
        self.checked.append(url)
        p = urllib.parse.urlsplit(url)
        if p.scheme not in ("http", "https"):
            raise PermissionError(f"scheme not allowed: {url!r}")
        host = (p.hostname or "").lower().rstrip(".")
        if host not in self.hosts:
            raise PermissionError(f"host out of scope: {host}")
        path = urllib.parse.unquote(p.path or "/")
        # collapse dot segments the way a real guard must, so an exclusion
        # cannot be walked past with '..'
        norm = urllib.parse.urljoin("/", path)
        for ex in self.exclude:
            if norm == ex or norm.startswith(ex + "/"):
                raise PermissionError(f"path excluded: {norm}")
        return p


class FakeProc:
    """Enough of Popen for `_spawn`: two readable pipes and a wait()."""

    _next_pid = 424242

    def __init__(self, stdout=b"", stderr=b"", rc=0, on_wait=None):
        self.stdout = io.BytesIO(stdout)
        self.stderr = io.BytesIO(stderr)
        self.returncode = rc
        self._on_wait = on_wait
        FakeProc._next_pid += 1
        self.pid = FakeProc._next_pid
        self.killed = False

    def wait(self, timeout=None):
        if self._on_wait is not None:
            self._on_wait(self, timeout)
        return self.returncode

    def poll(self):
        return self.returncode

    def kill(self):
        self.killed = True

    def terminate(self):            # pragma: no cover - not used
        self.killed = True


class Spawns:
    """Records every Popen call and hands back a scripted process."""

    def __init__(self, stdout=b"", stderr=b"", rc=0, on_wait=None,
                 per_tool=None):
        self.calls: list[tuple[tuple, dict]] = []
        self.stdout, self.stderr, self.rc = stdout, stderr, rc
        self.on_wait = on_wait
        self.per_tool = per_tool or {}
        self.lock = threading.Lock()

    def __call__(self, argv, **kwargs):
        # `argv` is Popen's first positional parameter - the list itself,
        # not a tuple of call args. Recorded as the list to stop the
        # double-indexing this double had on its first pass: `calls[i][0][0]`
        # read argv[0], every assertion compared a basename to a whole
        # command, and six tests failed for one reason that looked like six.
        with self.lock:
            self.calls.append((list(argv), dict(kwargs)))
        binary = os.path.basename(argv[0]) if argv else ""
        out = self.per_tool.get(binary, self.stdout)
        return FakeProc(stdout=out, stderr=self.stderr, rc=self.rc,
                        on_wait=self.on_wait)

    @property
    def argvs(self) -> list[list[str]]:
        return [c[0] for c in self.calls]

    def tools(self) -> list[str]:
        return [os.path.basename(a[0]) for a in self.argvs]


def abs_path(name: str) -> str:
    """A path that is absolute on POSIX AND on Windows.

    `/usr/bin/ffuf` is NOT absolute under `ntpath`: since Python 3.13 a path
    with exactly one leading slash is relative there. Measured here -
    `ntpath.isabs('/usr/bin/ffuf')` is False, `ntpath.isabs(r'C:\\t\\nmap.exe')`
    is True - so with a hardcoded POSIX path the Windows job in the CI
    matrix would have seen `available_tools()` refuse every faked tool, and
    every "the tool ran" assertion in this file would have failed there
    while passing here. `abspath` supplies the drive on Windows and
    normalises on POSIX; it touches no filesystem.
    """
    return os.path.abspath(os.path.join(os.sep, "fake-bin", name))


def install(monkeypatch, *names):
    """Pretend exactly these tools are installed, at absolute paths."""
    paths = {n: abs_path(n) for n in names}
    monkeypatch.setattr(orch.shutil, "which", lambda n: paths.get(n))
    return paths


def fake_spawns(monkeypatch, **kw) -> Spawns:
    spawns = Spawns(**kw)
    monkeypatch.setattr(orch.subprocess, "Popen", spawns)
    # Never signal a real process group from a test: the kill path takes a
    # pid, a FakeProc's pid is made up, and a made-up pid can belong to
    # something real on this host.
    monkeypatch.setattr(orch, "_kill_process_tree",
                        lambda proc: setattr(proc, "killed", True))
    return spawns


# ------------------------------------------------- the wiring, both ways


def test_recon_sweep_runs_the_tool_half_without_a_model(monkeypatch, tmp_path):
    """agent_fn=None: the tool half still runs, and the result says why
    the agent did not - the PASSING direction of the pair below."""
    install(monkeypatch, "ffuf")
    ffuf_out = (b'{"url":"http://target.test/admin","status":301,'
                b'"redirectlocation":"/admin/","host":"target.test"}\n')
    spawns = fake_spawns(monkeypatch, stdout=ffuf_out)
    scope = FakeScope()

    res = recon_sweep("http://target.test/", scope=scope, workdir=tmp_path,
                      tools=["ffuf"], agent_fn=None, timeout_s=30)

    assert isinstance(res, SweepResult)
    assert spawns.tools() == ["ffuf"], "the tool half must run regardless"
    assert res.agent_ran is False
    assert "no agent_fn" in res.agent_note and "model" in res.agent_note
    assert res.agent_suggestions == []
    assert "http://target.test/admin" in res.endpoints
    assert "http://target.test/admin/" in res.endpoints, \
        "redirectlocation is resolved against the url it came from"
    assert res.seconds >= 0.0
    run = res.tool_runs[0]
    assert run.skipped_reason == "" and run.rc == 0


def test_out_of_scope_target_never_spawns_a_process(monkeypatch, tmp_path):
    """The refusal that matters: no process, not a process that fails.

    Asserted on the mock rather than on the result, because a module that
    spawned the scan and then discarded the output would produce an
    identical SweepResult while the packets were already gone.
    """
    install(monkeypatch, "ffuf", "nmap", "nuclei")
    spawns = fake_spawns(monkeypatch)
    scope = FakeScope(hosts=["target.test"])

    res = recon_sweep("http://evil.test/", scope=scope, workdir=tmp_path,
                      agent_fn=lambda p: "/should-never-be-asked",
                      timeout_s=30)

    assert spawns.calls == [], "a refused target reached subprocess.Popen"
    assert res.endpoints == []
    assert res.tool_runs, "the refusal must be reported per tool, not hidden"
    for run in res.tool_runs:
        assert run.skipped_reason, f"{run.tool} has no skipped_reason"
        assert "out of scope" in run.skipped_reason or \
               "refused by scope guard" in run.skipped_reason
    assert res.agent_ran is False, \
        "the agent must not run for a target it may not act on"


def test_out_of_scope_endpoint_never_spawns_in_the_fanout(monkeypatch,
                                                          tmp_path):
    """Same refusal, per endpoint: one bad endpoint in a good list."""
    install(monkeypatch, "curl")
    spawns = fake_spawns(monkeypatch)
    scope = FakeScope(hosts=["target.test"])

    results = exploit_fanout(
        "http://target.test/",
        ["http://target.test/a", "http://evil.test/b",
         "http://target.test/c"],
        scope=scope, workdir=tmp_path, timeout_s=30, max_parallel=3)

    assert len(results) == 3, "one SweepResult per endpoint, in order"
    assert [r.target for r in results] == [
        "http://target.test/a", "http://evil.test/b", "http://target.test/c"]
    dialled = [a[-1] for a in spawns.argvs]
    assert "http://evil.test/b" not in dialled
    assert sorted(dialled) == ["http://target.test/a",
                               "http://target.test/c"]
    bad = results[1]
    assert bad.tool_runs and all(r.skipped_reason for r in bad.tool_runs)
    assert bad.endpoints == []


def test_an_excluded_path_is_refused_even_on_an_in_scope_host(monkeypatch,
                                                              tmp_path):
    """Scope is host AND path. An operator's --exclude is not advisory."""
    install(monkeypatch, "curl")
    spawns = fake_spawns(monkeypatch)
    scope = FakeScope(hosts=["target.test"], exclude=["/billing"])

    results = exploit_fanout("http://target.test/",
                             ["http://target.test/billing/pay",
                              "http://target.test/ok"],
                             scope=scope, workdir=tmp_path, timeout_s=30)

    dialled = [a[-1] for a in spawns.argvs]
    assert dialled == ["http://target.test/ok"]
    assert all(r.skipped_reason for r in results[0].tool_runs)


def test_a_missing_tool_is_a_skipped_reason_not_a_crash(monkeypatch,
                                                        tmp_path):
    """Nothing installed at all: a full result, every run explained."""
    install(monkeypatch)        # which() returns None for everything
    spawns = fake_spawns(monkeypatch)
    scope = FakeScope()

    res = recon_sweep("http://target.test/", scope=scope, workdir=tmp_path,
                      timeout_s=30)

    assert spawns.calls == []
    assert {r.tool for r in res.tool_runs} == {"nmap", "ffuf", "nuclei"}
    for run in res.tool_runs:
        assert "not installed" in run.skipped_reason
        assert run.argv == [] and run.rc is None
        assert isinstance(run.argv, list)
    # the declared target is still an endpoint: it was given, not inferred
    assert res.endpoints == ["http://target.test/"]


def test_an_unknown_tool_name_is_named_not_dropped(monkeypatch, tmp_path):
    """A typo'd tool must not read as 'that scanner found nothing'."""
    install(monkeypatch, "ffuf")
    fake_spawns(monkeypatch)
    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuff"], timeout_s=30)
    assert len(res.tool_runs) == 1
    assert "unknown tool" in res.tool_runs[0].skipped_reason


def test_the_faked_tool_path_is_absolute_on_this_platform():
    """A check on the harness, not on the module.

    Every "the tool ran" assertion in this file depends on
    `available_tools()` accepting the path `install()` fakes. When that path
    was hardcoded as '/usr/bin/ffuf' the dependency was invisible and wrong
    on Windows, where it is a RELATIVE path - so the whole file would have
    failed there in twenty confusing ways instead of one clear one.
    """
    assert os.path.isabs(abs_path("nmap"))
    assert os.path.basename(abs_path("nmap")) == "nmap"


def test_available_tools_refuses_a_relative_resolution(monkeypatch):
    """`which` returning './nmap' means a relative PATH entry.

    Every subprocess here runs with cwd=workdir, a directory the scanners
    write into, so a relative resolution is a binary chosen by the working
    directory. Refused, not abspath()ed.
    """
    monkeypatch.setattr(orch.shutil, "which",
                        lambda n: "./nmap" if n == "nmap" else None)
    assert available_tools() == {}

    nmap = abs_path("nmap")
    monkeypatch.setattr(orch.shutil, "which",
                        lambda n: nmap if n == "nmap" else None)
    assert available_tools() == {"nmap": nmap}


# ------------------------------------------------------- argv hygiene


def test_argv_is_a_list_and_shell_is_never_used(monkeypatch, tmp_path):
    """The target is attacker-influenced data; it is never syntax."""
    install(monkeypatch, "ffuf", "nmap", "nuclei")
    spawns = fake_spawns(monkeypatch)
    recon_sweep("http://target.test/x?q=1", scope=FakeScope(),
                workdir=tmp_path, timeout_s=30)

    assert spawns.calls, "nothing ran, so this test proved nothing"
    for argv, kwargs in spawns.calls:
        assert isinstance(argv, list), f"argv is {type(argv).__name__}"
        assert all(isinstance(tok, str) for tok in argv)
        assert not kwargs.get("shell"), "shell=True in a Popen call"
        assert kwargs.get("stdin") is subprocess.DEVNULL, \
            "a scanner must not inherit this process's stdin"


def test_no_call_in_the_module_can_reach_a_shell():
    """Checked on the AST, not on the text.

    A first version grepped the source for 'shell=True' and failed on the
    module's own docstring, which says it never passes it - the same mistake
    as asserting on a probe's verdict prose. The AST sees calls.
    """
    import ast

    src = (REPO / "argus" / "orchestrator.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned = {"system", "popen", "spawnl", "spawnv", "execl", "execv",
              "call", "check_call", "check_output", "run", "getoutput",
              "getstatusoutput"}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg == "shell":
                assert isinstance(kw.value, ast.Constant) and \
                    kw.value.value is False, "shell= passed a true value"
        name = ""
        if isinstance(node.func, ast.Attribute):
            name = node.func.attr
        elif isinstance(node.func, ast.Name):
            name = node.func.id
        if name in banned:
            mod = getattr(getattr(node.func, "value", None), "id", "")
            # subprocess.Popen is the one spawn primitive here, so the
            # deadline and the kill path are ones this module controls.
            assert not (mod in ("os", "subprocess") or name == "system"), \
                f"{mod}.{name} at line {node.lineno} bypasses Popen"


def test_a_scanner_does_not_inherit_credentials(monkeypatch, tmp_path):
    """A scanner is a semi-trusted child: nuclei executes templates, sqlmap
    runs its own payload code.

    Found by auditing this module, not by a failing test - `_spawn` passed
    no `env` at all, so every scanner inherited ANTHROPIC_API_KEY.
    `tools/analysis.py` has scrubbed this since
    `tests/test_external.py::test_run_external_env_scrubbed`, and a second
    spawn path that did not would make that test a claim about one code
    path rather than about the package.
    """
    install(monkeypatch, "ffuf")
    spawns = fake_spawns(monkeypatch, stdout=b"")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-should-not-be-inherited")
    monkeypatch.setenv("SOME_TOKEN", "t")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("PLAIN_VAR", "kept")

    recon_sweep("http://target.test/", scope=FakeScope(), workdir=tmp_path,
                tools=["ffuf"], timeout_s=20)

    assert spawns.calls, "nothing ran"
    env = spawns.calls[0][1].get("env")
    assert env is not None, "no env passed: the child inherits ours"
    for leaked in ("ANTHROPIC_API_KEY", "SOME_TOKEN", "DB_PASSWORD"):
        assert leaked not in env, f"{leaked} reached the scanner"
    assert env.get("PLAIN_VAR") == "kept", \
        "scrubbing must not strip the environment a tool needs"
    assert "PATH" in env, "a scanner needs PATH"
    assert not any("sk-should-not-be-inherited" in v
                   for v in env.values())


def test_a_target_that_reads_as_a_flag_is_refused(monkeypatch, tmp_path):
    """`-u` takes a VALUE. A value starting with '-' becomes an option.

    ffuf, nuclei and sqlmap all parse `-u <value>` that way, so an endpoint
    spelled `-oOUT` would turn a scan into a file write. Endpoints arrive
    from scanner output and from the model, i.e. from bytes the target
    chose, so this is checked rather than assumed.
    """
    install(monkeypatch, "curl")
    spawns = fake_spawns(monkeypatch)
    results = exploit_fanout("http://target.test/", ["-oEVIL"],
                             scope=FakeScope(), workdir=tmp_path,
                             timeout_s=30)
    assert spawns.calls == []
    assert "reads as a flag" in results[0].tool_runs[0].skipped_reason


def test_credentials_in_the_target_url_are_refused(monkeypatch, tmp_path):
    """argv is world-readable and is returned to the caller for its report.

    The package rule is that a declared credential never reaches an
    artifact. Refused rather than stripped: a stripped run would send
    unauthenticated requests and report them as authenticated ones.
    """
    install(monkeypatch, "curl", "nuclei", "sqlmap")
    spawns = fake_spawns(monkeypatch)
    res = recon_sweep("http://admin:hunter2@target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["nuclei"], timeout_s=30)
    assert spawns.calls == []
    assert "credentials in the URL" in res.agent_note
    for run in res.tool_runs:
        assert "credentials in the URL" in run.skipped_reason
        assert "hunter2" not in " ".join(run.argv)
    # and nowhere in the returned object either
    assert "hunter2" not in repr(res.tool_runs)


def test_sqlmap_is_detection_only(monkeypatch, tmp_path):
    """No --dump, no --os-shell, no --file-write, no stacked queries.

    This repository proves injection by reading what the query returns and
    stops there; stacked queries (sqlmap's 'S') execute a second statement,
    which is a write channel.
    """
    install(monkeypatch, "sqlmap")
    spawns = fake_spawns(monkeypatch)
    exploit_fanout("http://target.test/", ["http://target.test/p?id=1"],
                   scope=FakeScope(), workdir=tmp_path, timeout_s=30)
    argv = spawns.argvs[0]
    assert "--batch" in argv
    joined = " ".join(argv)
    for forbidden in ("--dump", "--os-shell", "--os-pwn", "--file-write",
                      "--file-read", "--tamper", "--eval", "--sql-shell"):
        assert forbidden not in joined, f"{forbidden} in sqlmap argv"
    tech = [a for a in argv if a.startswith("--technique")]
    assert tech == ["--technique=BEUT"], "S (stacked) and Q must stay out"
    assert any(a.startswith("--output-dir=") for a in argv), \
        "sqlmap session state belongs under the caller's workdir"


def test_no_tool_is_allowed_to_follow_a_redirect(monkeypatch, tmp_path):
    """A redirect target is chosen by the TARGET, and the guard never saw it.

    Measured against the loopback fixture, not reasoned about: sqlmap asked
    "got a 301 redirect to '...'. Do you want to follow? [Y/n]" and
    `--batch` answered Y, so it dialled a URL nothing had checked. curl is
    the same hole spelled `-L`, and a nuclei template can opt in.

    The Location header is in the captured output, so a caller can sweep it
    as an endpoint - where it IS checked.
    """
    install(monkeypatch, "curl", "nuclei", "sqlmap")
    spawns = fake_spawns(monkeypatch, stdout=b"")
    exploit_fanout("http://target.test/", ["http://target.test/p?id=1"],
                   scope=FakeScope(), workdir=tmp_path, timeout_s=30)

    by_tool = {os.path.basename(a[0]): a for a in spawns.argvs}
    assert set(by_tool) == {"curl", "nuclei", "sqlmap"}
    assert "-L" not in by_tool["curl"]
    assert "--location" not in by_tool["curl"]
    assert "--ignore-redirects" in by_tool["sqlmap"]
    assert "-dr" in by_tool["nuclei"]
    assert "-fr" not in by_tool["nuclei"]


def test_nmap_scans_the_port_the_operator_named(monkeypatch, tmp_path):
    """A port list that omits the target's own port cannot find anything.

    Measured: against the loopback fixture on :18080, a port outside the
    common list, nmap reported nothing at all - it never looked at the one
    port the target names.
    """
    install(monkeypatch, "nmap")
    spawns = fake_spawns(monkeypatch, stdout=b"")
    recon_sweep("http://target.test:18080/", scope=FakeScope(),
                workdir=tmp_path, tools=["nmap"], timeout_s=30)
    argv = spawns.argvs[0]
    ports = argv[argv.index("-p") + 1].split(",")
    assert "18080" in ports
    assert "80" in ports and "443" in ports, "the common list is still there"
    assert len(ports) == len(set(ports)), "a port listed twice"

    # the other direction: a target on a port already in the list must not
    # grow a duplicate entry
    spawns.calls.clear()
    recon_sweep("http://target.test:8080/", scope=FakeScope(),
                workdir=tmp_path, tools=["nmap"], timeout_s=30)
    argv = spawns.argvs[0]
    ports = argv[argv.index("-p") + 1].split(",")
    assert ports.count("8080") == 1


def test_nmap_needs_dash_6_for_an_ipv6_target(monkeypatch, tmp_path):
    """Measured: `nmap -Pn -sT -p 22 ::1` answers "::1 looks like an IPv6
    target specification -- you have to use the -6 option", scans nothing,
    and exits 0 - so an IPv6 engagement would have produced an empty recon
    run that looked successful."""
    install(monkeypatch, "nmap")
    spawns = fake_spawns(monkeypatch, stdout=b"")
    recon_sweep("http://[::1]:8080/", scope=FakeScope(hosts=["::1"]),
                workdir=tmp_path, tools=["nmap"], timeout_s=20)
    argv = spawns.argvs[0]
    assert "-6" in argv
    assert argv[-1] == "::1", "nmap takes the bare literal, not a URL"

    # the other direction: an IPv4 target must not get -6, which would make
    # nmap refuse it the same way
    spawns.calls.clear()
    recon_sweep("http://target.test/", scope=FakeScope(), workdir=tmp_path,
                tools=["nmap"], timeout_s=20)
    assert "-6" not in spawns.argvs[0]


def test_each_endpoint_gets_its_own_directory_and_cannot_escape_it(
        monkeypatch, tmp_path):
    """An endpoint string decides a directory name, so it must not be able
    to spell one. sqlmap keys its session files by host, so two endpoints on
    one host also must not share a directory."""
    install(monkeypatch, "sqlmap")
    spawns = fake_spawns(monkeypatch)
    wd = tmp_path / "work"
    exploit_fanout("http://target.test/",
                   ["http://target.test/../../../etc/a?id=1",
                    "http://target.test/b?id=1"],
                   scope=FakeScope(), workdir=wd, timeout_s=30,
                   max_parallel=2)

    outdirs = [a.split("=", 1)[1] for argv in spawns.argvs for a in argv
               if a.startswith("--output-dir=")]
    assert len(outdirs) == 2 and len(set(outdirs)) == 2
    for d in outdirs:
        resolved = Path(d).resolve()
        assert resolved != wd.resolve()
        assert wd.resolve() in resolved.parents, \
            f"{resolved} escaped the workdir"


# ------------------------------------------------------ bounded output


def test_output_truncation_holds(monkeypatch, tmp_path):
    """A target answering with a gigabyte must not cost this process.

    The reader keeps the cap and goes on READING the rest - closing the
    pipe instead would block the scanner in write() and the deadline would
    fire on a tool that had already finished its work.
    """
    install(monkeypatch, "ffuf")
    huge = b"A" * (orch._MAX_OUTPUT_CHARS * 3)
    spawns = fake_spawns(monkeypatch, stdout=huge,
                         stderr=b"E" * (orch._MAX_STDERR_CHARS * 3))
    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"], timeout_s=30)

    run = res.tool_runs[0]
    assert spawns.calls, "nothing ran"
    # the kept prefix plus the one-line marker, not the whole stream
    assert orch._MAX_OUTPUT_CHARS <= len(run.stdout) <= \
        orch._MAX_OUTPUT_CHARS + 200
    assert "output truncated" in run.stdout, \
        "a caller reading a parsed list has no other way to learn it is " \
        "partial"
    assert f"of {len(huge)} bytes" in run.stdout
    assert len(run.stderr) <= orch._MAX_STDERR_CHARS + 200


def test_a_torn_last_record_does_not_lose_the_whole_capture(monkeypatch,
                                                            tmp_path):
    """Truncation cuts mid-line, so the parser must survive half a record
    and still return the complete ones before it."""
    install(monkeypatch, "ffuf")
    good = b'{"url":"http://target.test/a","status":200}\n'
    torn = b'{"url":"http://target.test/b","sta'
    fake_spawns(monkeypatch, stdout=good + torn)
    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"], timeout_s=30)
    assert "http://target.test/a" in res.endpoints
    assert "http://target.test/b" not in res.endpoints


def test_the_deadline_kills_the_tree_and_keeps_partial_output(monkeypatch,
                                                              tmp_path):
    """A timed-out scanner has usually already emitted its findings, and
    anything it spawned must not outlive it: an orphan goes on talking to
    the target with no scope guard and no place in the transcript."""
    install(monkeypatch, "nuclei")
    killed: list = []

    def on_wait(proc, timeout):
        raise subprocess.TimeoutExpired(cmd="nuclei", timeout=timeout)

    spawns = Spawns(stdout=b'{"template-id":"x","matched-at":'
                           b'"http://target.test/found"}\n',
                    on_wait=on_wait)
    monkeypatch.setattr(orch.subprocess, "Popen", spawns)
    monkeypatch.setattr(orch, "_kill_process_tree", killed.append)

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["nuclei"], timeout_s=5)

    assert len(killed) == 1, "the process group was not killed"
    run = res.tool_runs[0]
    assert run.rc is None, "a killed process has no exit status"
    assert "killed after" in run.stderr
    assert "http://target.test/found" in res.endpoints, \
        "partial output from a killed scanner is still evidence"


def test_a_failed_spawn_is_a_skipped_run(monkeypatch, tmp_path):
    """The binary can vanish between `which` and `Popen`. One tool failing
    to start must not lose the other tools' results."""
    install(monkeypatch, "ffuf", "nuclei")

    def popen(args, **kw):
        if "ffuf" in args[0]:
            raise FileNotFoundError(2, "No such file or directory", args[0])
        return FakeProc(stdout=b"")

    monkeypatch.setattr(orch.subprocess, "Popen", popen)
    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf", "nuclei"],
                      timeout_s=30)
    by_tool = {r.tool: r for r in res.tool_runs}
    assert "spawn failed" in by_tool["ffuf"].skipped_reason
    assert by_tool["nuclei"].skipped_reason == ""


# -------------------------------------------------------- concurrency


def test_exploit_fanout_really_runs_endpoints_concurrently(monkeypatch,
                                                           tmp_path):
    """Asserted twice, because wall-clock alone proves nothing.

    A barrier: it can only be passed if that many endpoints are in flight
    at the same moment, so a serial implementation deadlocks on it and the
    test fails instead of merely being slow.

    Then the recorded windows: [started, started + seconds] per run, both
    read off `time.monotonic()`, must actually intersect. That is the same
    reconstruction a caller would use, so it checks the FIELDS and not just
    the behaviour.
    """
    install(monkeypatch, "curl")        # exactly one process per endpoint
    n = 3
    barrier = threading.Barrier(n, timeout=20)

    def on_wait(proc, timeout):
        barrier.wait()                  # BrokenBarrierError if serialised

    spawns = Spawns(stdout=b"HTTP/1.1 200 OK\r\n\r\nok", on_wait=on_wait)
    monkeypatch.setattr(orch.subprocess, "Popen", spawns)

    eps = [f"http://target.test/{i}" for i in range(n)]
    results = exploit_fanout("http://target.test/", eps, scope=FakeScope(),
                             workdir=tmp_path, timeout_s=30, max_parallel=n)

    assert len(results) == n
    assert len(spawns.calls) == n
    runs = [r.tool_runs[0] for r in results]
    assert all(r.skipped_reason == "" for r in runs)

    def overlaps(a: ToolRun, b: ToolRun) -> bool:
        return (a.started < b.started + b.seconds
                and b.started < a.started + a.seconds)

    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    assert all(overlaps(runs[i], runs[j]) for i, j in pairs), \
        "recorded windows do not intersect: " + \
        repr([(r.started, r.seconds) for r in runs])


def test_max_parallel_one_is_actually_serial(monkeypatch, tmp_path):
    """The other direction of the same measurement.

    If the overlap test above could pass without concurrency, this one
    would fail - the windows it reads are the same fields, recorded the
    same way, and here they must NOT intersect.
    """
    install(monkeypatch, "curl")

    def on_wait(proc, timeout):
        time.sleep(0.05)

    spawns = Spawns(stdout=b"ok", on_wait=on_wait)
    monkeypatch.setattr(orch.subprocess, "Popen", spawns)

    eps = [f"http://target.test/{i}" for i in range(3)]
    results = exploit_fanout("http://target.test/", eps, scope=FakeScope(),
                             workdir=tmp_path, timeout_s=30, max_parallel=1)

    runs = sorted((r.tool_runs[0] for r in results), key=lambda r: r.started)
    for a, b in zip(runs, runs[1:]):
        assert a.started + a.seconds <= b.started + 1e-6, \
            "max_parallel=1 overlapped two endpoints"


def test_max_parallel_zero_does_not_crash(monkeypatch, tmp_path):
    """A degenerate argument is clamped, not turned into a ValueError out
    of ThreadPoolExecutor."""
    install(monkeypatch, "curl")
    fake_spawns(monkeypatch, stdout=b"ok")
    results = exploit_fanout("http://target.test/",
                             ["http://target.test/a"], scope=FakeScope(),
                             workdir=tmp_path, timeout_s=30, max_parallel=0)
    assert len(results) == 1 and results[0].tool_runs[0].skipped_reason == ""


def test_the_agent_half_overlaps_the_tool_half(monkeypatch, tmp_path):
    """The agent must not wait for the slowest scanner.

    With a wait-for-all seed there is no overlap left to exploit, which is
    why the agent is seeded from what has landed inside a short grace
    window. Measured here: the agent is called while the tool is still
    inside wait().
    """
    install(monkeypatch, "ffuf")
    monkeypatch.setattr(orch, "_AGENT_SEED_GRACE_S", 0.05)
    in_wait = threading.Event()
    release = threading.Event()
    seen: dict = {}

    def on_wait(proc, timeout):
        in_wait.set()
        release.wait(timeout=20)

    spawns = Spawns(stdout=b"", on_wait=on_wait)
    monkeypatch.setattr(orch.subprocess, "Popen", spawns)

    def agent(prompt):
        seen["tool_still_running"] = in_wait.is_set() and not release.is_set()
        seen["prompt"] = prompt
        release.set()
        return "/from-the-agent"

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"], agent_fn=agent,
                      timeout_s=30)

    assert seen.get("tool_still_running") is True, \
        "the agent half ran only after the tool half had finished"
    assert "pending tools: ffuf" in seen["prompt"]
    assert res.agent_ran is True
    assert "http://target.test/from-the-agent" in res.endpoints


def test_the_fanout_prompt_names_the_endpoint_not_just_the_engagement(
        monkeypatch, tmp_path):
    """Asking the model to extend evidence from /admin while telling it the
    subject is / is how a suggestion ends up irrelevant.

    The first version passed only the engagement target, so every endpoint
    in a fan-out got the same prompt header.
    """
    install(monkeypatch, "curl")
    fake_spawns(monkeypatch, stdout=b"HTTP/1.1 200 OK\r\n\r\nhi")
    prompts: list[str] = []

    exploit_fanout("http://target.test/",
                   ["http://target.test/admin?id=1"], scope=FakeScope(),
                   workdir=tmp_path, timeout_s=20,
                   agent_fn=lambda p: prompts.append(p) or "/x")

    assert prompts, "the agent half never ran"
    head = prompts[0]
    assert "http://target.test/admin?id=1" in head
    assert "engagement target is http://target.test/" in head


def test_a_repeated_tool_name_is_not_silently_collapsed(monkeypatch,
                                                        tmp_path):
    """`slots` and the future map are keyed by tool name, so tools=["ffuf",
    "ffuf"] used to return one run for two requested and the caller could
    not tell which."""
    install(monkeypatch, "ffuf")
    spawns = fake_spawns(monkeypatch, stdout=b"")
    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf", "ffuf"], timeout_s=20)
    assert [r.tool for r in res.tool_runs] == ["ffuf"]
    assert len(spawns.calls) == 1


def test_a_hung_agent_does_not_hold_the_sweep_open(monkeypatch, tmp_path):
    """A thread cannot be cancelled, so a hung agent_fn is bounded by
    abandoning it. The sweep must still return, with the tool half's
    results and a note saying what happened."""
    install(monkeypatch, "ffuf")
    release = threading.Event()
    try:
        fake_spawns(monkeypatch, stdout=b'{"url":"http://target.test/a"}\n')

        def agent(prompt):
            release.wait(timeout=30)
            return "too late"

        started = time.monotonic()
        res = recon_sweep("http://target.test/", scope=FakeScope(),
                          workdir=tmp_path, tools=["ffuf"], agent_fn=agent,
                          timeout_s=5)
        assert time.monotonic() - started < 25
        assert res.agent_ran is False
        assert "did not return within" in res.agent_note
        assert "http://target.test/a" in res.endpoints, \
            "the tool half's results survive a hung agent"
    finally:
        release.set()       # never leave the worker parked in the suite


def test_an_agent_that_raises_is_a_note_not_a_traceback(monkeypatch,
                                                        tmp_path):
    """The model path fails for reasons outside this process - no key, a
    rate limit, a 529 - and that must not lose the tool half."""
    install(monkeypatch, "ffuf")
    fake_spawns(monkeypatch, stdout=b'{"url":"http://target.test/a"}\n')

    def agent(prompt):
        raise RuntimeError("no API key configured")

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"], agent_fn=agent,
                      timeout_s=30)
    assert res.agent_ran is False
    assert "RuntimeError" in res.agent_note and "no API key" in res.agent_note
    assert "http://target.test/a" in res.endpoints


# ------------------------------------------- the agent's wordlist, gated


def test_the_agent_wordlist_becomes_a_second_ffuf_run(monkeypatch, tmp_path):
    """The whole point of the module: a tool is only as good as the
    wordlist it was handed, so the agent writes one from what was observed
    and ffuf runs again on it. Both runs stay visible in tool_runs."""
    install(monkeypatch, "ffuf")
    per_tool = {"ffuf": b'{"url":"http://target.test/admin-v1"}\n'}
    spawns = fake_spawns(monkeypatch, per_tool=per_tool)

    def agent(prompt):
        assert "admin-v1" in prompt, "the agent must read the real output"
        return "admin-v2\nadmin-v3\n/api/v2/users"

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"], agent_fn=agent,
                      timeout_s=30)

    assert spawns.tools() == ["ffuf", "ffuf"], \
        "the agent's wordlist did not produce a second ffuf run"
    tools = [r.tool for r in res.tool_runs]
    assert tools == ["ffuf", "ffuf-agent"]
    second = res.tool_runs[1]
    wl = second.argv[second.argv.index("-w") + 1]
    words = Path(wl).read_text(encoding="utf-8").split()
    assert words == ["admin-v2", "admin-v3", "api/v2/users"]
    assert res.agent_suggestions == ["admin-v2", "admin-v3", "/api/v2/users"]


def test_an_agent_suggestion_off_host_never_reaches_the_endpoints(
        monkeypatch, tmp_path):
    """The agent reads bytes the TARGET chose, so a suggestion is a
    suggestion: the guard decides, not the model."""
    install(monkeypatch, "ffuf")
    spawns = fake_spawns(monkeypatch, stdout=b"")

    def agent(prompt):
        return ("http://evil.test/exfil\n"
                "//evil.test/protocol-relative\n"
                "/legitimate\n")

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"], agent_fn=agent,
                      timeout_s=30)

    assert res.agent_ran is True
    assert "http://evil.test/exfil" in res.agent_suggestions, \
        "what the model said is reported verbatim"
    assert res.endpoints == ["http://target.test/",
                             "http://target.test/legitimate"]
    for argv in spawns.argvs:
        assert "evil.test" not in " ".join(argv)
    # The protocol-relative line is the interesting one. It names another
    # host by URL semantics, so it must be REFUSED - not stripped into
    # 'http://target.test/evil.test/protocol-relative', which is what the
    # first version of `_suggestion_endpoints` produced: an in-scope
    # endpoint nobody proposed, with the refusal hidden.
    assert not any("evil.test" in ep for ep in res.endpoints)


def test_an_agent_word_is_scope_checked_as_the_url_ffuf_would_request(
        monkeypatch, tmp_path):
    """ffuf substitutes the word itself, so the word is the only thing that
    can be refused before the request exists.

    A word that lands inside an operator exclusion would otherwise be sent
    with no guard ever seeing it: there is no per-request hook in ffuf.

    The boundary is the guard's, not this module's - which is why
    `escapes-the-fuzz-directory` below is KEPT. `../../etc/passwd` resolves
    to a path on an in-scope host that no exclusion covers, so the guard
    allows it, and inventing a second "stay under the target's directory"
    policy the operator never declared would be this module overruling the
    object it was handed.
    """
    install(monkeypatch, "ffuf")
    spawns = fake_spawns(monkeypatch, stdout=b"")
    scope = FakeScope(hosts=["target.test"], exclude=["/billing"])

    def agent(prompt):
        return ("safe-word\n"
                "billing/pay\n"              # straight into the exclusion
                "x/../billing/refund\n"      # the same, spelled around it
                "-oEVIL\n"                   # reads as an ffuf flag
                "with space\n"               # prose, not a token
                "ctrl\u0007word\n"           # a control character
                + "z" * 500 + "\n"           # unbounded
                + "../etc/passwd\n")         # in scope: the guard allows it

    res = recon_sweep("http://target.test/", scope=scope,
                      workdir=tmp_path, tools=["ffuf"], agent_fn=agent,
                      timeout_s=30)

    agent_runs = [r for r in res.tool_runs if r.tool == "ffuf-agent"]
    assert agent_runs, "no agent wordlist run to inspect"
    wl = agent_runs[0].argv[agent_runs[0].argv.index("-w") + 1]
    words = Path(wl).read_text(encoding="utf-8").split()
    assert words == ["safe-word", "../etc/passwd"], \
        f"refused words reached the list: {words}"
    for refused in ("billing/pay", "x/../billing/refund", "-oEVIL",
                    "with space", "z" * 500):
        assert refused not in words
    assert not any(w.startswith("-") for w in words), \
        "a wordlist entry must not be able to read as a flag"
    assert not any("\u0007" in w for w in words)
    assert len(spawns.calls) == 2
    # the refused words are still reported as what the model said
    assert "billing/pay" in res.agent_suggestions


def test_agent_output_that_is_prose_degrades_instead_of_raising(monkeypatch,
                                                                tmp_path):
    """A model that answers with paragraphs should cost nothing. Not a JSON
    contract on purpose: this half is best-effort."""
    install(monkeypatch, "ffuf")
    fake_spawns(monkeypatch, stdout=b"")
    long_prose = "I would suggest, based on the output above, " * 20

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"],
                      agent_fn=lambda p: long_prose, timeout_s=30)
    assert res.agent_ran is True
    assert res.agent_suggestions == []
    assert "no usable lines" in res.agent_note


def test_agent_suggestions_are_capped(monkeypatch, tmp_path):
    """A model talked into emitting a hundred thousand lines costs a
    bounded amount of this process and a bounded number of requests."""
    install(monkeypatch, "ffuf")
    fake_spawns(monkeypatch, stdout=b"")
    many = "\n".join(f"/p{i}" for i in range(10_000))
    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"],
                      agent_fn=lambda p: many, timeout_s=30)
    assert len(res.agent_suggestions) == orch._MAX_AGENT_SUGGESTIONS
    assert len(res.endpoints) <= orch._MAX_ENDPOINTS


def test_a_non_callable_agent_is_reported(monkeypatch, tmp_path):
    install(monkeypatch, "ffuf")
    fake_spawns(monkeypatch, stdout=b"")
    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"],
                      agent_fn="not a function", timeout_s=30)
    assert res.agent_ran is False and "not callable" in res.agent_note


def test_the_prompt_carries_no_credential_and_no_whole_stream(monkeypatch,
                                                              tmp_path):
    """The prompt is bounded: a gigabyte of scanner output must not become
    a gigabyte of context."""
    install(monkeypatch, "ffuf")
    fake_spawns(monkeypatch, stdout=b"B" * (orch._MAX_OUTPUT_CHARS * 2))
    seen = {}
    recon_sweep("http://target.test/", scope=FakeScope(), workdir=tmp_path,
                tools=["ffuf"], agent_fn=lambda p: seen.setdefault("p", p),
                timeout_s=30)
    assert len(seen["p"]) < orch._MAX_PROMPT_EVIDENCE + 4000


# ------------------------------------------------------------- parsers
#
# The records below were captured from the real tools on this host. If a
# field name here is wrong, the parser is reading something that does not
# exist and the endpoint list is silently empty.


def test_ffuf_jsonl_is_parsed_from_the_url_field():
    """ffuf 2.1.0-dev, `-json`. `input.FUZZ` is BASE64 on this code path
    and plain text under `-of json`, so the URL has to come from `url` -
    rebuilding it from the input word would yield '/YWRtaW4=' here."""
    line = ('{"input":{"FFUFHASH":"MjJjMjQx","FUZZ":"YWRtaW4="},'
            '"position":1,"status":301,"length":0,"words":1,"lines":1,'
            '"content-type":"","redirectlocation":"/admin/",'
            '"url":"http://127.0.0.1:18080/admin","duration":2897143,'
            '"scraper":{},"resultfile":"","host":"127.0.0.1:18080"}')
    assert orch._parse_ffuf_jsonl(line) == [
        "http://127.0.0.1:18080/admin", "http://127.0.0.1:18080/admin/"]
    assert orch._parse_ffuf_jsonl("not json at all\n\n") == []


def test_nuclei_jsonl_is_parsed_from_matched_at():
    """nuclei v3.11.0, `-jsonl -silent`. `url` is the input target and is
    identical for every record; `matched-at` is where the match was."""
    line = ('{"template-id":"fixture-any-200","info":{"name":"f",'
            '"author":["fixture"],"tags":["fixture"],"severity":"info"},'
            '"type":"http","host":"127.0.0.1","port":"18080",'
            '"scheme":"http","url":"http://127.0.0.1:18080/","path":"/",'
            '"matched-at":"http://127.0.0.1:18080/robots.txt",'
            '"ip":"127.0.0.1","timestamp":"2026-11-18T02:35:33-05:00",'
            '"curl-command":"curl ...","matcher-status":true}')
    assert orch._parse_nuclei_jsonl(line) == [
        "http://127.0.0.1:18080/robots.txt"]


def test_a_nuclei_stats_line_is_not_a_finding():
    """`-stats` puts JSON progress lines on the same stream. They have no
    template-id, and counting one as a finding would invent an endpoint."""
    stats = ('{"duration":"0:00:02","errors":"0","hosts":"1","matched":"0",'
             '"percent":"100","requests":"55","rps":"25",'
             '"startedAt":"2026-11-18T02:42:22-05:00","templates":"51",'
             '"total":"55"}')
    assert orch._parse_nuclei_jsonl(stats) == []


def test_nmap_grepable_takes_the_scheme_from_the_observed_service():
    """nmap 7.95, `-oG -`. Port fields are
    port/state/proto/owner/service/rpc/version.

    This is the line the fixture scan really produced, trailing
    `Ignored State` field and all - that field follows the port list on the
    same line, separated by a tab, and a parser that split the whole
    remainder on ',' would be relying on its value never containing one.
    """
    line = ("Host: 127.0.0.1 (TranTien)\tPorts: "
            "18080/open/tcp//http//SimpleHTTPServer 0.6 (Python 3.14.6)/"
            "\tIgnored State: closed (78)")
    assert orch._parse_nmap_grepable(line, "target.test") == [
        "http://target.test:18080/"]
    mixed = (line.replace("closed (78)", "closed (70), filtered (8)"))
    assert orch._parse_nmap_grepable(mixed, "target.test") == [
        "http://target.test:18080/"]
    tls = "Host: 1.2.3.4 ()\tPorts: 443/open/tcp//ssl|http///"
    assert orch._parse_nmap_grepable(tls, "target.test") == [
        "https://target.test:443/"]


def test_nmap_does_not_guess_a_scheme_or_trust_the_ptr_name():
    """Measured on this host: an unprivileged `-sT` scan of 18080 reports
    `18080/open/tcp/////` - no service token at all - and the same scan
    with `-sV` reports `http`. '8080 is probably http' is an invention, so
    a port with no service yields nothing.

    And the name in parentheses is the PTR record, which the target's own
    reverse DNS chooses. Using it would let a target put a hostname of its
    choosing into the endpoint list.
    """
    no_service = "Host: 127.0.0.1 (evil-ptr.test)\tPorts: 18080/open/tcp/////"
    assert orch._parse_nmap_grepable(no_service, "target.test") == []

    with_service = ("Host: 127.0.0.1 (evil-ptr.test)\tPorts: "
                    "8080/open/tcp//http///")
    out = orch._parse_nmap_grepable(with_service, "target.test")
    assert out == ["http://target.test:8080/"]
    assert not any("evil-ptr" in u for u in out)

    closed = "Host: 1.2.3.4 ()\tPorts: 80/closed/tcp//http///"
    assert orch._parse_nmap_grepable(closed, "target.test") == []


def test_endpoints_are_normalised_and_deduplicated():
    """One spelling per endpoint, or the fan-out scans the same URL twice."""
    scope = FakeScope(hosts=["target.test"])
    merged = orch._merge_endpoints(scope, [
        "http://target.test:80/a",
        "http://TARGET.test/a",
        "http://target.test/a#frag",
        "https://target.test:443/b",
        "http://target.test/c?id=1",
        "http://target.test/c?id=2",
        "ftp://target.test/x",
        "http://evil.test/y",
        "",
        None,
    ])
    assert merged == ["http://target.test/a", "https://target.test/b",
                      "http://target.test/c?id=1", "http://target.test/c?id=2"]


def test_merge_caps_the_endpoint_count():
    """A target that answers every path with 200 makes ffuf emit one record
    per wordlist line; the fan-out that follows must stay bounded."""
    scope = FakeScope(hosts=["target.test"])
    many = [f"http://target.test/p{i}" for i in range(orch._MAX_ENDPOINTS * 3)]
    assert len(orch._merge_endpoints(scope, many)) == orch._MAX_ENDPOINTS


def test_a_guard_that_raises_something_unexpected_still_refuses():
    """Fail-closed means fail-closed. Catching only the declared exception
    type would turn a bug inside the guard into an allow."""

    class BrokenScope:
        def check(self, url):
            raise TypeError("someone changed my signature")

    assert orch._scope_ok(BrokenScope(), "http://target.test/")
    assert orch._merge_endpoints(BrokenScope(),
                                 ["http://target.test/a"]) == []


# -------------------------------------------------- against the real guard


def test_the_real_scope_guard_satisfies_the_contract(monkeypatch, tmp_path):
    """The fake above could agree with a wrong assumption about the real
    object. This runs one sweep through `argus.scope.ScopeGuard` itself.

    Offline: the target is an IP literal, so no name is resolved, and an
    out-of-scope host is refused on the allowlist before any lookup.
    """
    from argus.scope import ScopeGuard

    install(monkeypatch, "curl")
    spawns = fake_spawns(monkeypatch, stdout=b"ok")
    guard = ScopeGuard("http://127.0.0.1:18080/", allow_private=True)

    results = exploit_fanout("http://127.0.0.1:18080/",
                             ["http://127.0.0.1:18080/ok",
                              "http://evil.test/no"],
                             scope=guard, workdir=tmp_path, timeout_s=30,
                             max_parallel=2)

    dialled = [a[-1] for a in spawns.argvs]
    assert dialled == ["http://127.0.0.1:18080/ok"]
    assert all(r.skipped_reason for r in results[1].tool_runs)
    assert results[0].endpoints == ["http://127.0.0.1:18080/ok"]


def test_tool_names_are_a_subset_of_the_allowlist():
    """Two lists, one concept: `tools.analysis._ALLOWED_TOOLS` is the
    package's answer to which binaries this agent may start, and this
    module must not be able to drift past it.

    Asserted between the REAL lists rather than by importing one into the
    other: `tools.analysis` pulls in `proof` and `httpclient`, and the
    orchestrator's claim is that it needs no network stack.
    """
    from argus.tools.analysis import _ALLOWED_TOOLS

    extra = set(orch._TOOL_NAMES) - set(_ALLOWED_TOOLS)
    assert not extra, f"{sorted(extra)} would bypass the tool allowlist"
    assert set(orch._BUILDERS) == set(orch._TOOL_NAMES)
    assert set(orch._PARSERS) == set(orch._TOOL_NAMES)


def test_httpx_is_not_in_the_tool_table():
    """The binary called `httpx` on this host is the PYTHON httpx CLI
    (`#!/usr/bin/python3`, a URL fetcher), not ProjectDiscovery's prober:
    it takes no `-json` and emits no JSONL. A fan-out that shelled out to
    'httpx' would silently run the wrong program - and it is not in the
    package allowlist either.

    Asserted on the structures, not on the source text: a first pass here
    grepped the file for the string and failed on the comment that explains
    why the tool is absent, which is testing prose.
    """
    for table in (orch._TOOL_NAMES, orch._BUILDERS, orch._PARSERS,
                  orch._RECON_TOOLS, orch._EXPLOIT_TOOLS):
        assert "httpx" not in table


def test_importing_the_module_pulls_in_no_llm_client_and_no_http_stack():
    """The module must stay testable with no key and no network, which is
    a claim about its IMPORTS, not about its behaviour.

    Checked in a fresh interpreter: this test session has already imported
    httpx through conftest, so asserting on `sys.modules` here would pass
    for the wrong reason.

    This test failed when it was first written, and the module was wrong,
    not the test: `from .tools._subproc import _kill_tree` runs
    `argus/tools/__init__.py`, which imports the whole tool registry and
    with it httpclient, proof and httpx. The import is now lazy, on the
    timeout path - see `_kill_process_tree`.
    """
    code = ("import sys; import argus.orchestrator; "
            "print(sorted(m for m in ('httpx', 'anthropic', 'argus.llm', "
            "'argus.proof', 'argus.httpclient', 'argus.tools.registry', "
            "'argus.mcp') "
            "if m in sys.modules))")
    out = subprocess.run([sys.executable, "-c", code], cwd=str(REPO),
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "[]", \
        f"importing the orchestrator loaded {out.stdout.strip()}"


# ============================================================================
# Second audit pass. Every test below this line failed against the module as
# written, and each names the defect it holds down. They are kept as a block
# rather than filed into the sections above so that the pass is readable as
# one thing: six defects, five of them reachable from bytes the target or the
# model chose.
# ============================================================================


# ------------------------------------- 1. a parse that raises loses the sweep


def test_a_malformed_port_in_tool_output_does_not_lose_the_sweep(monkeypatch,
                                                                 tmp_path):
    """`ParseResult.port` parses ON ACCESS and raises.

    DEFECT: `_norm_endpoint` guarded `urlsplit` and then read `p.port`
    outside the guard. `urlsplit` accepts `http://h:99999/` - it does not
    look at the port - and `.hostname` answers happily, so the `ValueError`
    lands on the `port` line, comes out of `_merge_endpoints`, out of
    `_sweep` and out of `recon_sweep`.

    Repro before the fix, with exactly the stdout below:
        ValueError: Port out of range 0-65535

    One ffuf record chosen by the target therefore destroyed the whole
    sweep: the other tools' endpoints, the captured bytes, the timings. The
    module says "one malformed record must not lose the other tools'
    endpoints" and wrapped each PARSER to mean it, but the merge that reads
    what the parsers return was the unguarded step.
    """
    install(monkeypatch, "ffuf")
    out = (b'{"url":"http://target.test/good","status":200}\n'
           b'{"url":"http://target.test:99999/bad","status":200}\n'
           b'{"url":"http://target.test:notanumber/also-bad","status":200}\n'
           b'{"url":"http://target.test/good-too","status":200}\n')
    spawns = fake_spawns(monkeypatch, stdout=out)

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"], timeout_s=30)

    assert spawns.calls, "nothing ran"
    assert res.tool_runs[0].skipped_reason == ""
    assert "http://target.test/good" in res.endpoints
    assert "http://target.test/good-too" in res.endpoints, \
        "a record AFTER the malformed one was lost"
    assert not any("99999" in ep for ep in res.endpoints)
    assert not any("notanumber" in ep for ep in res.endpoints)


def test_an_unreadable_candidate_is_dropped_not_raised():
    """The unit, both directions: unreadable means "not an endpoint"."""
    for bad in ("http://h:99999/x", "http://h:abc/x", "http://[::1",
                "http://[::1]:99999/", "", "   ", "not-a-url"):
        assert orch._norm_endpoint(bad) == "", bad
    assert orch._norm_endpoint("http://H:80/a") == "http://h/a"
    assert orch._norm_endpoint("http://[::1]:8080/a") == "http://[::1]:8080/a"

    scope = FakeScope(hosts=["target.test"])
    merged = orch._merge_endpoints(scope, [
        "http://target.test/a", "http://target.test:99999/b",
        "http://target.test/c"])
    assert merged == ["http://target.test/a", "http://target.test/c"]


def test_an_agent_suggestion_that_cannot_be_resolved_does_not_lose_the_sweep(
        monkeypatch, tmp_path):
    """DEFECT: `urljoin` PARSES its second argument, so a model line can
    raise out of the sweep.

    Measured: `urljoin('http://target.test/', '//[::1')` raises
    `ValueError: Invalid IPv6 URL`, and that raise came out of
    `recon_sweep` from `_suggestion_endpoints`. `http://[::1` raises from
    the other call site, `_agent_words`, which is the one place a word can
    be refused before ffuf substitutes it.

    Both are one line of model output. The agent half is seeded with bytes
    the target chose, so this is the target's line as much as the model's -
    and the cost was the tool half's results, which is precisely what
    `_call_agent`'s own `except` exists to prevent.
    """
    install(monkeypatch, "ffuf")
    spawns = fake_spawns(monkeypatch,
                         stdout=b'{"url":"http://target.test/real"}\n')

    def agent(prompt):
        return ("//[::1\n"              # raises in _suggestion_endpoints
                "http://[::1\n"         # raises in _agent_words
                "/survivor\n"
                "usable-word\n")

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"], agent_fn=agent,
                      timeout_s=30)

    assert res.agent_ran is True
    assert "http://target.test/real" in res.endpoints, \
        "the tool half's results were lost to a model line"
    assert "http://target.test/survivor" in res.endpoints
    assert not any("[::1" in ep for ep in res.endpoints)
    # and the usable word still became the second pass
    agent_runs = [r for r in res.tool_runs if r.tool == "ffuf-agent"]
    assert agent_runs and agent_runs[0].skipped_reason == ""
    wl = agent_runs[0].argv[agent_runs[0].argv.index("-w") + 1]
    words = Path(wl).read_text(encoding="utf-8").split()
    # `[::1` is the `//[::1` line after `lstrip('/')`, and `urljoin` resolves
    # THAT without raising - as a path segment, not a netloc. So it is a word
    # the guard was asked about and allowed, and it stays: refusing it here
    # would be this module inventing a rule the operator never declared,
    # the same boundary `../etc/passwd` sits on in the test above. The line
    # that cannot be resolved is the one that gets dropped, and only that.
    assert words == ["[::1", "survivor", "usable-word"], words
    assert len(spawns.calls) == 2


# ------------------------------- 2. the flag guard did not cover every path


def test_nmap_never_receives_a_flag_shaped_host(monkeypatch, tmp_path):
    """DEFECT: the one argv token no separator can protect was unchecked.

    `_plan` calls `_reject_flagish` on the URL each builder says it will
    dial. For ffuf, nuclei, sqlmap and curl that URL IS the argv token (and
    curl adds `--`), so the guard covers them. nmap takes the host as a
    BARE POSITIONAL and nmap has no `--`, and the URL `_argv_nmap` returned
    for the check was `http://<host>` - which can never begin with '-'. So
    the guard that exists for exactly this threat was unreachable on the
    only path that needed it.

    Measured on nmap 7.95 with the token the builder produced for
    `http://-oG.target.test/` (`urlsplit().hostname` lower-cases it):

        $ nmap -Pn -sT --open -sV -p 80 --host-timeout 10s -oG - \
               -og.target.test
        # Nmap 7.95 scan initiated ... as: ... -oG - -og.target.test
        WARNING: No targets were specified, so 0 hosts scanned.
        $ ls
        g.target.test

    nmap read it as `-oG og.target.test`: it wrote its grepable output to
    a local file in the workdir, scanned nothing, and exited 0. The sweep
    reported an nmap run with rc=0, no error and no endpoints - the
    "empty, successful-looking recon run" this builder already refuses for
    IPv6 - and the module's own docstring names the file-write as the
    threat the guard is for.
    """
    install(monkeypatch, "nmap", "ffuf", "nuclei")
    spawns = fake_spawns(monkeypatch, stdout=b"")
    scope = FakeScope(hosts=["-og.target.test"])        # the guard allows it

    res = recon_sweep("http://-oG.target.test/", scope=scope,
                      workdir=tmp_path, tools=["nmap"], timeout_s=30)

    assert spawns.calls == [], \
        f"nmap was spawned with {spawns.argvs}"
    reason = res.tool_runs[0].skipped_reason
    assert "reads as a flag" in reason and "positional" in reason, reason

    # The other direction, same scope object: an ordinary host still runs,
    # so this is a refusal of the token and not of nmap.
    spawns.calls.clear()
    recon_sweep("http://target.test/", scope=FakeScope(), workdir=tmp_path,
                tools=["nmap"], timeout_s=30)
    assert len(spawns.calls) == 1
    assert spawns.argvs[0][-1] == "target.test"


def test_the_real_guard_allows_a_dash_leading_subdomain():
    """Why the test above is not a hypothetical.

    `ScopeGuard.include_subdomains` defaults to True and matches on
    `host.endswith("." + allowed)`, so for the target `target.test` the host
    `-oG.target.test` is IN SCOPE - the guard is doing its job, the host is
    a subdomain. A host like that reaches the orchestrator from a redirect
    `Location`, a nuclei `matched-at`, or a model suggestion, i.e. from
    bytes the target chose.

    Offline: the guard is built on an IP literal so construction resolves
    nothing, `extra_hosts` adds a name without a lookup, and
    `allow_private=True` short-circuits the resolution inside `check`.
    """
    from argus.scope import ScopeGuard

    guard = ScopeGuard("http://127.0.0.1/", extra_hosts=["target.test"],
                       allow_private=True)
    assert guard.include_subdomains is True
    assert guard.host_allowed("-og.target.test") is True
    assert guard.check("http://-oG.target.test/x") is not None


def test_no_builder_puts_a_target_derived_flag_token_in_argv():
    """The generalisation, over the REAL builder table.

    Asserted against `_BUILDERS` itself rather than against a list of tool
    names written here, so a sixth tool added to the table has to satisfy
    it too. The invariant is the module's own sentence, applied token by
    token: a flag-shaped host must either be refused outright, or appear
    only inside a token that does not ITSELF read as a flag.
    `http://-oevil.target.test/x` is a URL and is safe in any position;
    the bare `-oevil.target.test` is an option in every position.

    The first version of this test asked instead whether the token was
    "protected" by the token before it - after `--`, or after a single-dash
    flag that takes a value - and it passed against the unfixed nmap
    builder, because the token before the host was nmap's `-oG` VALUE,
    the string `-`. A heuristic about the PRECEDING token cannot tell a
    flag from a flag's value, and a vacuous guard test is worse than none:
    it was the only test in this file that failed to notice the defect
    next door. The property below needs no such inference.
    """
    hostile = "-oevil.target.test"
    target = f"http://{hostile}/x?id=1"
    checked = 0
    for name, builder in sorted(orch._BUILDERS.items()):
        built = builder(abs_path(name), target, "/tmp/wd", "", 30)
        if isinstance(built, str):
            assert "flag" in built, f"{name} refused for another reason"
            checked += 1
            continue
        argv, _dial = built
        assert isinstance(argv, list) and all(isinstance(t, str)
                                              for t in argv)
        for i, tok in enumerate(argv[1:], start=1):
            if hostile not in tok:
                continue            # one of the tool's own flags
            assert not tok.startswith("-"), \
                f"{name}: argv[{i}]={tok!r} is read as an option, not a host"
            checked += 1
    assert checked >= len(orch._BUILDERS), \
        "a builder neither refused the host nor placed it anywhere"


# ------------------------------ 3. the child's cwd is not the parent's cwd


def test_a_relative_path_is_absolutised_for_the_child(monkeypatch, tmp_path):
    """DEFECT: every child runs with `cwd` set to the workdir, so a
    relative path meant one directory in this process and another in the
    child.

    `_argv_ffuf` answers `Path(wl).is_file()` in THIS process's cwd and
    then handed the relative string to a child whose cwd is the workdir.
    Measured, with cwd=<tmp> and workdir='work':

        -w   'lists/w.txt'          cwd 'work'
        the child would read 'work/lists/w.txt'   exists: False

    So the operator's own wordlist was silently not used, and the
    `wordlist not found` refusal whose whole job is to catch that had
    already passed against the real file. ffuf then fails on its own and
    the sweep reports a tool run that found nothing - in a module whose
    entire thesis is about which wordlist you hand the scanner.

    sqlmap's `--output-dir=` and the agent's `mkstemp` wordlist had the
    same break, which is why the workdir is absolutised once in `_sweep`.
    """
    monkeypatch.chdir(tmp_path)
    (tmp_path / "lists").mkdir()
    (tmp_path / "lists" / "w.txt").write_text("admin\n", encoding="utf-8")
    install(monkeypatch, "ffuf")
    spawns = fake_spawns(monkeypatch, stdout=b"")

    recon_sweep("http://target.test/", scope=FakeScope(), workdir="work",
                tools=["ffuf"], wordlist="lists/w.txt", timeout_s=30)

    assert spawns.calls, "nothing ran"
    argv, kwargs = spawns.calls[0]
    wl = argv[argv.index("-w") + 1]
    assert os.path.isabs(wl), f"-w {wl!r} is relative to nothing the child knows"
    assert os.path.isabs(str(kwargs["cwd"]))
    # the only assertion that matters: resolved the way the CHILD would
    assert Path(os.path.join(str(kwargs["cwd"]), wl)).is_file()


def test_the_agent_wordlist_and_sqlmap_outdir_are_absolute(monkeypatch,
                                                           tmp_path):
    """The same break on the two paths that build a path from the workdir
    instead of from the operator's argument."""
    monkeypatch.chdir(tmp_path)
    install(monkeypatch, "ffuf", "sqlmap")
    spawns = fake_spawns(monkeypatch, stdout=b"")

    recon_sweep("http://target.test/", scope=FakeScope(), workdir="wd-rel",
                tools=["ffuf"], agent_fn=lambda p: "admin-v2\nadmin-v3",
                timeout_s=30, wordlist=str(tmp_path / "lists.txt")
                if (tmp_path / "lists.txt").write_text("a\n",
                                                       encoding="utf-8")
                is None else "")

    agent_argv = [a for a in spawns.argvs if "agent-words-" in " ".join(a)]
    assert agent_argv, "no agent wordlist run"
    wl = agent_argv[0][agent_argv[0].index("-w") + 1]
    assert os.path.isabs(wl) and Path(wl).is_file()

    spawns.calls.clear()
    exploit_fanout("http://target.test/", ["http://target.test/p?id=1"],
                   scope=FakeScope(), workdir="wd-rel2", timeout_s=30)
    outdirs = [a.split("=", 1)[1] for argv in spawns.argvs for a in argv
               if a.startswith("--output-dir=")]
    assert outdirs and all(os.path.isabs(d) for d in outdirs), outdirs


# ------------------------- 4. "abandoned" was not true of a pool worker


def test_the_agent_runs_on_a_daemon_thread(monkeypatch, tmp_path):
    """DEFECT: a hung agent_fn held the whole process open at exit.

    The module bounds a hung `agent_fn` by abandoning it, since a Python
    thread cannot be cancelled. That word was false: the call ran on a
    `ThreadPoolExecutor` worker, and `concurrent.futures.thread` registers
    `_python_exit` with `threading._register_atexit`, which JOINS every
    pool worker at interpreter shutdown.

    Measured end to end, agent_fn sleeping, timeout_s=5:

        sweep returned after 5.0s, agent_ran=False
        falling off the end of main now
        exit rc=124 after 25s          <- killed; it could not exit

    The sweep came back with the honest note and the engagement process
    still hung forever, which is the exact failure the note claims to
    prevent. After the fix the same script exits rc=0 in 5s.

    Asserted as the daemon flag rather than by hanging a subprocess for 25
    seconds: the flag IS the mechanism - a daemon thread is not joined at
    exit - and this costs milliseconds.
    """
    install(monkeypatch, "ffuf")
    fake_spawns(monkeypatch, stdout=b"")
    seen: dict = {}

    def agent(prompt):
        t = threading.current_thread()
        seen["daemon"] = t.daemon
        return "/x"

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"], agent_fn=agent,
                      timeout_s=30)
    assert res.agent_ran is True
    assert seen.get("daemon") is True, \
        "the agent half runs on a non-daemon thread, so an abandoned call " \
        "is joined at interpreter exit and the process cannot exit"


def test_an_abandoned_agent_leaves_only_a_daemon_thread(monkeypatch,
                                                        tmp_path):
    """The same claim, measured on the thread that is actually abandoned.

    The sweep returns while this agent is still parked, so the thread is
    observable here - and it has to be a daemon, or the interpreter will
    wait for it.
    """
    install(monkeypatch, "ffuf")
    release = threading.Event()
    try:
        monkeypatch.setattr(orch, "_AGENT_SEED_GRACE_S", 0.05)
        fake_spawns(monkeypatch, stdout=b'{"url":"http://target.test/a"}\n')

        res = recon_sweep("http://target.test/", scope=FakeScope(),
                          workdir=tmp_path, tools=["ffuf"],
                          agent_fn=lambda p: release.wait(timeout=30),
                          timeout_s=5)

        assert res.agent_ran is False
        assert "did not return within" in res.agent_note
        parked = [t for t in threading.enumerate() if t.name == "argus-agent"]
        assert parked, "the abandoned thread is gone: this proved nothing"
        for t in parked:
            assert t.daemon is True, \
                "a non-daemon agent thread is joined at interpreter exit"
    finally:
        release.set()


def test_a_base_exception_from_the_agent_is_a_note_not_a_lost_sweep(
        monkeypatch, tmp_path):
    """`_call_agent` catches Exception, which is right - but the future's
    `.result()` re-raised anything else straight through `_sweep`, losing
    the tool half for a class of raise the agent half is not even supposed
    to decide about. Reading the result out of the box instead of out of a
    future closes that with no change to what Exception means.

    And the REASON has to be the raise. The first version of this fix let
    such a raise fall through to the abandonment note - "agent_fn did not
    return within 5s of stage budget" - for a call that had returned, by
    raising, in a millisecond. A false reason in the honest-looking field
    is worse than a missing one, and the interpreter also printed an
    unhandled-thread traceback that nothing in the result referred to.
    """
    install(monkeypatch, "ffuf")
    fake_spawns(monkeypatch, stdout=b'{"url":"http://target.test/a"}\n')

    class Boom(BaseException):
        pass

    def agent(prompt):
        raise Boom("not an Exception subclass")

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"], agent_fn=agent,
                      timeout_s=5)
    assert res.agent_ran is False
    assert "Boom" in res.agent_note and "raised" in res.agent_note, \
        res.agent_note
    assert "did not return" not in res.agent_note, \
        "a call that raised is reported as one that never came back"
    assert "http://target.test/a" in res.endpoints, \
        "the tool half's results were lost"


def test_no_argus_thread_outlives_a_sweep_or_a_fanout(monkeypatch, tmp_path):
    """Threads are joined, not leaked - including when one endpoint's sweep
    raises.

    `_sweep` is written not to raise, so the raise is injected: one
    endpoint's merge blows up, the other endpoints' results still come
    back, and nothing is left running.
    """
    install(monkeypatch, "curl")
    fake_spawns(monkeypatch, stdout=b"ok")
    before = {t.ident for t in threading.enumerate()}

    real_merge = orch._merge_endpoints

    def exploding_merge(scope, candidates):
        if any("boom" in str(c) for c in candidates):
            raise RuntimeError("injected: a sweep that raises")
        return real_merge(scope, candidates)

    monkeypatch.setattr(orch, "_merge_endpoints", exploding_merge)
    results = exploit_fanout("http://target.test/",
                             ["http://target.test/a",
                              "http://target.test/boom",
                              "http://target.test/c"],
                             scope=FakeScope(), workdir=tmp_path,
                             timeout_s=30, max_parallel=3)

    assert [r.target for r in results] == ["http://target.test/a",
                                           "http://target.test/boom",
                                           "http://target.test/c"]
    assert "sweep failed" in results[1].agent_note
    assert results[0].endpoints and results[2].endpoints
    leaked = [t.name for t in threading.enumerate()
              if t.ident not in before and t.name.startswith("argus-")]
    assert leaked == [], f"threads left running: {leaked}"


# ----------------------- 5. the operator's tool selection binds both halves


def test_the_tools_selection_binds_the_agent_wordlist_pass(monkeypatch,
                                                           tmp_path):
    """DEFECT: `tools=` restricted the tool half and not the agent's extra
    ffuf run.

    The second pass asked `available_tools()` - what the HOST has - instead
    of what the operator selected, so `recon_sweep(tools=["nuclei"])` with
    an agent spawned ffuf anyway. Measured, with both binaries installed
    and a one-tool selection: binaries spawned `['nuclei', 'ffuf']`.

    In scope and rate-limited, but not asked for: an engagement that
    forbids directory brute-forcing forbids it here too, and `tools=` is
    where an operator says so.
    """
    install(monkeypatch, "ffuf", "nuclei")     # both present on the host
    spawns = fake_spawns(monkeypatch, stdout=b"")

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["nuclei"],
                      agent_fn=lambda p: "admin-backup\n/api/v2",
                      timeout_s=30)

    assert spawns.tools() == ["nuclei"], \
        f"a tool the operator did not select ran: {spawns.tools()}"
    # named, not dropped: the caller must be able to see that the words
    # were generated and never fuzzed
    by_tool = {r.tool: r for r in res.tool_runs}
    assert "ffuf-agent" in by_tool
    assert "not fuzzed" in by_tool["ffuf-agent"].skipped_reason
    assert "tools=" in by_tool["ffuf-agent"].skipped_reason
    assert res.agent_suggestions == ["admin-backup", "/api/v2"]

    # the other direction: select ffuf and the second pass runs
    spawns.calls.clear()
    res2 = recon_sweep("http://target.test/", scope=FakeScope(),
                       workdir=tmp_path, tools=["ffuf"],
                       agent_fn=lambda p: "admin-backup", timeout_s=30)
    assert spawns.tools() == ["ffuf", "ffuf"]
    assert [r.tool for r in res2.tool_runs] == ["ffuf", "ffuf-agent"]
    assert res2.tool_runs[1].skipped_reason == ""


def test_an_agent_word_that_cannot_be_fuzzed_is_still_reported(monkeypatch,
                                                               tmp_path):
    """ffuf absent from the host: the thesis cannot execute, and the result
    has to say so rather than report suggestions nobody acted on."""
    install(monkeypatch, "nuclei")              # no ffuf anywhere
    fake_spawns(monkeypatch, stdout=b"")
    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf", "nuclei"],
                      agent_fn=lambda p: "admin-backup", timeout_s=30)
    by_tool = {r.tool: r for r in res.tool_runs}
    assert "not installed" in by_tool["ffuf"].skipped_reason
    assert "not fuzzed" in by_tool["ffuf-agent"].skipped_reason
    assert "not installed" in by_tool["ffuf-agent"].skipped_reason


# ------------------------- 6. model text, as data, all the way to argv


def test_a_flag_shaped_or_control_laden_suggestion_never_reaches_argv(
        monkeypatch, tmp_path):
    """Model output is target-chosen data. The caps and the sanitising are
    asserted on what ACTUALLY ran, not on the parsed list.

    `--config=/etc/passwd` is the second shape of the same threat as
    `-oOUT`: ffuf, nuclei and sqlmap all have a `--config`-style option
    that reads a file of further options, so one accepted token would hand
    the model the rest of the command line.
    """
    install(monkeypatch, "ffuf")
    spawns = fake_spawns(monkeypatch, stdout=b"")
    hostile = ["-oOUT", "--config=/etc/passwd", "-of", "--", "-",
               "ok\u0007bell", "ok‮override", "tab\there",
               "nul\x00byte", "a" * 500, "fine-word"]

    res = recon_sweep("http://target.test/", scope=FakeScope(),
                      workdir=tmp_path, tools=["ffuf"],
                      agent_fn=lambda p: "\n".join(hostile), timeout_s=30)

    assert spawns.calls, "nothing ran"
    all_tokens = [tok for argv in spawns.argvs for tok in argv]
    for bad in ("-oOUT", "--config=/etc/passwd", "/etc/passwd"):
        assert bad not in all_tokens, f"{bad} reached argv"
    assert not any("\u0007" in t or "‮" in t or "\x00" in t
                   for t in all_tokens)

    agent_runs = [r for r in res.tool_runs if r.tool == "ffuf-agent"]
    assert agent_runs and agent_runs[0].skipped_reason == ""
    wl = agent_runs[0].argv[agent_runs[0].argv.index("-w") + 1]
    words = Path(wl).read_text(encoding="utf-8").splitlines()
    assert words == ["fine-word"], words
    # the control-character lines never even survive parsing, so they are
    # not reported as suggestions either
    assert "ok\u0007bell" not in res.agent_suggestions
    assert "-oOUT" in res.agent_suggestions, \
        "what the model said is still reported verbatim to the caller"


def test_every_endpoint_returned_was_approved_by_the_guard(monkeypatch,
                                                           tmp_path):
    """The whole merge, from three untrusted sources at once.

    ffuf's `url` and `redirectlocation`, nuclei's `matched-at` and the
    model's lines all name locations, and the guard must have said yes to
    every one that comes back - checked against the recorded calls on the
    guard itself, so an endpoint that reached the list without being asked
    about fails here.
    """
    install(monkeypatch, "ffuf", "nuclei")
    per_tool = {
        "ffuf": (b'{"url":"http://target.test/a","redirectlocation":'
                 b'"http://evil.test/steal"}\n'),
        "nuclei": (b'{"template-id":"t","matched-at":'
                   b'"http://evil.test/matched"}\n'
                   b'{"template-id":"t","matched-at":'
                   b'"http://target.test/b"}\n'),
    }
    spawns = fake_spawns(monkeypatch, per_tool=per_tool)
    scope = FakeScope(hosts=["target.test"], exclude=["/private"])

    res = recon_sweep("http://target.test/", scope=scope, workdir=tmp_path,
                      tools=["ffuf", "nuclei"],
                      agent_fn=lambda p: "/private/keys\n/c", timeout_s=30)

    assert len(spawns.calls) >= 2
    assert res.endpoints == ["http://target.test/", "http://target.test/a",
                             "http://target.test/b", "http://target.test/c"]
    for ep in res.endpoints:
        assert ep in scope.checked, f"{ep} was never put to the guard"
    assert not any("evil.test" in ep for ep in res.endpoints)
    assert not any("private" in ep for ep in res.endpoints)


def test_a_builder_whose_dial_url_differs_is_scope_checked_too(monkeypatch,
                                                               tmp_path):
    """`_plan` checks each builder's OWN dial URL, and that check was dead
    in this file until a planted regression showed it.

    Removing the `_scope_ok` call from `_plan` passed all 64 other tests
    here, because every out-of-scope case in them is caught one step
    earlier by the sweep-level check on the target. The two builders whose
    dial URL is not the target URL are the ones that need it:

      * nmap scans a HOST - its dial URL drops the port and the path.
      * ffuf fuzzes a DIRECTORY - its dial URL drops the last path
        segment and the query.

    `ScopeGuard` is host-and-path based and would allow both, so the guard
    below is a stricter one - an engagement authorising exactly one
    endpoint on one port, which is a real shape for an authorisation note
    and exactly the case where a duck-typed guard is handed in. nuclei
    dials the endpoint itself and runs; the other two must not start a
    process, and must still show the caller the argv that was refused.
    """

    class OneEndpointScope:
        """Authorises one exact origin+path and nothing else."""

        def __init__(self, allowed):
            self.allowed = allowed
            self.checked: list[str] = []

        def check(self, url):
            self.checked.append(url)
            if url != self.allowed:
                raise PermissionError(
                    f"this engagement authorises only {self.allowed}")
            return urllib.parse.urlsplit(url)

    target = "http://target.test:8443/app/x"
    install(monkeypatch, "nmap", "ffuf", "nuclei")
    spawns = fake_spawns(monkeypatch, stdout=b"")
    scope = OneEndpointScope(target)

    res = recon_sweep(target, scope=scope, workdir=tmp_path,
                      tools=["nmap", "ffuf", "nuclei"], timeout_s=30)

    assert spawns.tools() == ["nuclei"], \
        f"a process was started for a URL the guard refused: {spawns.argvs}"
    by_tool = {r.tool: r for r in res.tool_runs}
    assert by_tool["nuclei"].skipped_reason == ""
    for tool in ("nmap", "ffuf"):
        reason = by_tool[tool].skipped_reason
        assert "out of scope" in reason, f"{tool}: {reason!r}"
        # documented behaviour: the caller can see what WOULD have run
        assert by_tool[tool].argv, f"{tool} refusal dropped its argv"
        assert by_tool[tool].rc is None
    # the guard was asked about the dial URLs, not about something near them
    assert "http://target.test" in scope.checked, "nmap's host URL"
    assert "http://target.test:8443/app/" in scope.checked, "ffuf's base URL"


def test_agent_ran_and_agent_note_say_different_things(monkeypatch,
                                                       tmp_path):
    """`agent_ran` answers "did the half run"; `agent_note` answers "why
    not, or what came of it". The five cases, in one place, because the
    field comment used to say the note was only ever a reason for NOT
    running - and the module sets it, truthfully, on a run that returned
    nothing usable too.
    """
    install(monkeypatch, "ffuf")
    fake_spawns(monkeypatch, stdout=b"")
    common = dict(scope=FakeScope(), workdir=tmp_path, tools=["ffuf"],
                  timeout_s=30)

    def sweep(agent_fn):
        return recon_sweep("http://target.test/", agent_fn=agent_fn, **common)

    cases = [
        (None, False, "no agent_fn"),
        ("not a callable", False, "not callable"),
        (lambda p: (_ for _ in ()).throw(RuntimeError("boom")), False,
         "RuntimeError"),
        (lambda p: "", False, "no text"),
        (lambda p: 42, False, "no text"),
        (lambda p: "I think, on balance, that " * 30, True, "no usable lines"),
    ]
    for agent_fn, ran, fragment in cases:
        res = sweep(agent_fn)
        assert res.agent_ran is ran, (agent_fn, res.agent_note)
        assert fragment in res.agent_note, (fragment, res.agent_note)
        assert res.agent_suggestions == []
        assert res.tool_runs[0].skipped_reason == "", \
            "the tool half must run whatever the agent half does"

    # and the one case where the note is empty: it ran and said something
    res = sweep(lambda p: "/found-by-the-model")
    assert res.agent_ran is True and res.agent_note == ""
    assert res.agent_suggestions == ["/found-by-the-model"]
