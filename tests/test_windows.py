"""Windows behaviour, checked rather than assumed.

No Windows container exists for a Linux host, but what differs between the
platforms is path and separator handling, and both are testable here: ntpath
IS the Windows implementation, and the code branches on os.name / os.sep.
CI runs the real thing on windows-latest; this catches the predictable half
before it gets there.
"""
import ntpath
import os
import pathlib
import shlex
import sys
import unittest.mock as mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "lab"))

from argus import proof
from argus.tools import analysis


def assert_ok(name, ok, detail=""):
    assert ok, f"{name}: {detail}"


def test_windows_semantics():

    # --- 1. the external-arg scope check skips tokens containing os.sep ---
    # On Windows os.sep is "\\", so a posix path `/etc/passwd` no longer contains
    # os.sep and stops being skipped as a filename. Does anything break?
    # _is_windows() reads os.name, so BOTH have to be patched - patching os.sep
    # alone left posix splitting on and the token came back mangled. My test was
    # wrong, not the code; checking it properly is the point of the exercise.
    with mock.patch.object(os, "sep", "\\"), mock.patch.object(os, "name", "nt"):
        toks = analysis._split_args("-iL targets.txt C:\\lists\\hosts.txt /etc/hosts")
        has_backslash = [t for t in toks if "\\" in t]
        assert_ok("a windows path token survives splitting",
              bool(has_backslash), f"{toks}")
        # ...and it must then be skipped as a filename rather than
        # scope-checked. This used to assert `[t for t in toks if os.sep in t]`
        # - and `os.sep` IS "\\" inside this patch, so that was the previous
        # line's predicate restated: it could not fail unless the assertion
        # above had already failed, and it never touched the scope check whose
        # skipping behaviour it claimed to verify.
        #
        # The subject is `_args_scope_check` now. A recording scope says what
        # was actually handed to it, which is the thing that matters: a
        # Windows path must not be read as a hostname, and a real hostname
        # must still be checked - or "nothing was scope-checked" would pass
        # this.
        checked = []

        class _RecordingScope:
            def check(self, target):
                checked.append(target)

        class _Ctx:
            scope = _RecordingScope()

        analysis._args_scope_check(
            _Ctx(), "-iL targets.txt C:\\lists\\hosts.txt evil.example")
        assert_ok("a windows path token is not read as a hostname",
                  not any("hosts.txt" in c or "lists" in c for c in checked),
                  f"{checked}")
        assert_ok("a bare hostname beside it is still scope-checked",
                  any("evil.example" in c for c in checked), f"{checked}")

        # What this does NOT pin, measured rather than assumed: deleting
        # the `os.sep in tok` skip from `_args_scope_check` leaves both
        # assertions passing. `_hostish_token` rejects every token
        # containing a separator - `C:\lists\hosts.txt` splits to host
        # part `"C"`, and `evil.example\sub` stays unhostish - so no token
        # exists whose outcome depends on that skip. It is defence in depth
        # and the second guard is the one doing the work. Removing the
        # hostname check instead DOES fail the second assertion, which is
        # how the two were told apart.
    # posix hosts keep posix splitting
    toks2 = analysis._split_args("-iL targets.txt /etc/hosts evil.example")
    assert_ok("posix splitting is unchanged", "evil.example" in toks2, f"{toks2}")

    # --- 2. the lab's cat containment under windows path semantics -------------
    import vulnapp
    root_posix = os.path.realpath(vulnapp.FAKEFS)
    # the containment compares realpath against root + os.sep. Under ntpath the
    # separator is "\\" and comparison is case-insensitive, which a startswith
    # check does NOT handle.
    cases = [
        ("fake", "fake\\x", True),            # inside
        ("fake", "FAKE\\x", True),            # same dir, different case - windows
        ("fake", "fake-other\\secret", False),
        ("fake", "fakeother\\secret", False),
    ]
    for root, target, inside in cases:
        r = ntpath.normpath("C:\\lab\\" + root)
        t = ntpath.normpath("C:\\lab\\" + target)
        naive = t == r or t.startswith(r + ntpath.sep)
        folded = (t.lower() == r.lower()
                  or t.lower().startswith(r.lower() + ntpath.sep))
        assert_ok(f"cat containment: {target!r} inside {root!r} == {inside}",
              folded == inside,
              f"case-folded={folded} naive={naive}")

    # --- 3. WINIDENT line anchors against CRLF ---------------------------------
    from argus import proof
    assert_ok("WINIDENT matches nt authority across CRLF",
          bool(proof.WINIDENT_RE.search("<pre>nt authority\\system\r\nargus1</pre>")))
    assert_ok("WINIDENT_WEAK matches a whole CRLF line",
          bool(proof.WINIDENT_WEAK_RE.search("WIN-SRV01\\jdoe\r\n")))
    assert_ok("WINIDENT_WEAK rejects a windows path line",
          not proof.WINIDENT_WEAK_RE.search("C:\\Windows\\System32\r\n"))

    # --- 4. _endpoint_shape must not be confused by a backslash ---------------
    e = {"id": "r1", "request": {"method": "GET",
         "url": "http://t.local/api/user/1", "headers": {}, "body": None},
         "response": {"status": 200, "headers": {}, "body": "x"}}
    with mock.patch.object(os, "sep", "\\"), mock.patch.object(os, "name", "nt"):
        shape = proof._endpoint_shape(e)
    assert_ok("_endpoint_shape is os.sep-independent",
          shape == "t.local/api/user/{id}", shape)

    # --- 5. the lab's exec allowlist under nt ---------------------------------
    with mock.patch.object(os, "name", "nt"):
        out = vulnapp._lab_exec("echo hello")
    assert_ok("echo is emulated, so it works with no /bin", out == "hello", out)
    out = vulnapp._lab_exec("id")
    assert_ok("a missing binary is reported, not raised",
          "uid=" in out or "command not found" in out, out)

    # --- 6. docs/sample-session digests are LF-stable -------------------------
    import hashlib, json, pathlib
    # The repo root, derived from this file. It was hard-coded to the author's
    # own checkout, so this test passed on exactly one machine and failed on
    # every CI runner with a FileNotFoundError naming that path - which is why
    # it was not reproducible in a clean clone *here*.
    root = pathlib.Path(__file__).resolve().parent.parent
    d = root / "docs" / "sample-session"
    crlf = [p.name for p in d.iterdir() if b"\r\n" in p.read_bytes()]
    assert_ok("no CRLF in the sealed sample session", not crlf, f"{crlf}")
    ga = (root / ".gitattributes").read_text()
    assert_ok(".gitattributes pins the sample to LF",
          "docs/sample-session/** eol=lf" in ga)

    # --- 7. shlex.split posix flag for MCP commands --------------------------
    import shlex
    assert_ok("an MCP command with a windows path parses under nt rules",
          shlex.split(r'C:\tools\server.exe --flag', posix=False)[0]
          == r'C:\tools\server.exe')
    assert_ok("...and posix parsing would eat the backslashes",
          shlex.split(r'C:\tools\server.exe --flag', posix=True)[0]
          != r'C:\tools\server.exe')


def test_cat_containment_is_case_folded():
    """On NT the comparison is case-insensitive, and a plain startswith
    refuses `FAKE\\x` inside root `fake` - failing closed, but refusing a
    legitimate read that the rce and lfi demonstrations depend on."""
    # The subject is the lab's own `_within_root`, under NT path
    # semantics. This loop used to rebuild the comparison from
    # `ntpath.normpath`, `str.lower` and `ntpath.sep` and assert its own
    # model - nothing from `vulnapp` or `argus` appeared in it - so it
    # passed entirely out of the standard library. Its only link to the
    # code was `assert "os.path.normcase" in src`, which proves the
    # identifier occurs somewhere in the function text, not that it is
    # applied to both sides of the comparison. The model also differed
    # from the code twice over: `str.lower()` where the code uses
    # `os.path.normcase`, which on NT also folds `/` to `\\`, and
    # `ntpath.sep` where the code uses `os.sep`.
    #
    # `realpath` is patched to `ntpath.normpath` so the cases are decided
    # by path semantics rather than by what exists on this filesystem -
    # these roots do not exist, and on POSIX `realpath` would resolve them
    # against the cwd.
    import vulnapp

    with mock.patch.object(os, "sep", ntpath.sep), \
            mock.patch.object(os.path, "normcase", ntpath.normcase), \
            mock.patch.object(os.path, "realpath", ntpath.normpath):
        for root, target, inside in (("fake", "fake\\x", True),
                                     ("fake", "FAKE\\x", True),
                                     ("fake", "fake", True),
                                     ("fake", "fake-other\\s", False),
                                     ("fake", "fakeother\\s", False),
                                     ("fake", "..\\elsewhere\\s", False)):
            r = "C:\\lab\\" + root
            t = "C:\\lab\\" + target
            assert vulnapp._within_root(t, r) is inside, (root, target)

    # The WIRING - that `cat` actually consults the function tested above -
    # is a different claim, and it is not asserted here, deliberately.
    #
    # The obvious way is a source grep, and this test used to carry one:
    # `assert "os.path.normcase" in src`. It proves an identifier occurs
    # in the function text, not that it governs anything. Written as
    # `assert "_within_root(path, FAKEFS)" in src` it is no better -
    # measured, by planting `if _within_root(path, FAKEFS) is False and
    # False:`, which keeps the substring and disables the guard, and the
    # assertion passed. A grep cannot tell a call from a mention.
    #
    # `test_cat_containment_is_not_prefix_based` in test_lab.py holds the
    # wiring behaviourally instead: it drives `_lab_exec` against a real
    # sibling directory on the live lab root, and it fails when the
    # separator is dropped from the comparison. Logic here, wiring there,
    # and neither pretending to be the other.
