#!/usr/bin/env python3
"""Offline proof that tools/pwn/ is right, against binaries already on disk.

Ground truth is readelf, which IS present here, so each case compares the
pure-python parse to what readelf reports rather than to an expectation typed
by hand. Run: python3 tools/pwn/selftest.py
"""
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pwnstatic import elf as _elf              # noqa: E402
from pwnstatic import gadgets as _gad          # noqa: E402
from pwnstatic import protections as _prot     # noqa: E402

RESULTS = []


def case(name):
    def deco(fn):
        try:
            detail = fn()
            RESULTS.append(("PASS", name, detail))
        except AssertionError as exc:
            RESULTS.append(("FAIL", name, str(exc)))
        except SkipTest as exc:
            RESULTS.append(("SKIP", name, str(exc)))
        return fn
    return deco


class SkipTest(Exception):
    pass


def readelf(*args):
    try:
        return subprocess.run(["readelf", *args], capture_output=True,
                              text=True, timeout=30).stdout
    except (OSError, subprocess.SubprocessError):
        raise SkipTest("readelf unavailable")


def pick(*candidates):
    for c in candidates:
        if os.path.isfile(c):
            return c
    raise SkipTest("no candidate binary present: " + ", ".join(candidates))


LS = None
LIBC = None


@case("elf_header_matches_readelf")
def _t1():
    path = pick("/bin/ls", "/usr/bin/ls")
    e = _elf.load(path)
    out = readelf("-hW", path)
    entry = int(re.search(r"Entry point address:\s+0x([0-9a-f]+)", out).group(1), 16)
    assert e.entry == entry, "entry %s != readelf %s" % (hex(e.entry), hex(entry))
    assert ("ELF64" in out) == (e.bits == 64), "bit width disagrees with readelf"
    assert e.machine == "x86-64" or "X86-64" not in out, "machine disagrees"
    return {"binary": path, "entry": hex(entry), "bits": e.bits}


@case("needed_libraries_match_readelf")
def _t2():
    path = pick("/bin/ls", "/usr/bin/ls")
    e = _elf.load(path)
    out = readelf("-d", path)
    want = re.findall(r"\(NEEDED\)\s+Shared library: \[([^\]]+)\]", out)
    assert e.needed() == want, "%r != readelf %r" % (e.needed(), want)
    assert want, "readelf reported no NEEDED at all; the case proves nothing"
    return {"needed": want}


@case("nx_and_relro_match_readelf_segments")
def _t3():
    path = pick("/bin/ls", "/usr/bin/ls")
    e = _elf.load(path)
    prot = _prot.protections(e)
    segs = readelf("-lW", path)
    stack = re.search(r"GNU_STACK.*?(RW?E?|R E|RWE)\s+0x", segs)
    has_relro = "GNU_RELRO" in segs
    stack_x = bool(stack and "E" in stack.group(1))
    assert prot["nx"]["value"] == (not stack_x), \
        "nx=%s but readelf GNU_STACK flags=%r" % (prot["nx"]["value"],
                                                  stack and stack.group(1))
    assert (prot["relro"]["value"] != "none") == has_relro, \
        "relro=%s but GNU_RELRO present=%s" % (prot["relro"]["value"], has_relro)
    bind_now = bool(re.search(r"BIND_NOW|FLAGS.*NOW", readelf("-d", path)))
    assert (prot["relro"]["value"] == "full") == (has_relro and bind_now), \
        "full RELRO claimed without BIND_NOW"
    return {"nx": prot["nx"]["value"], "relro": prot["relro"]["value"],
            "bind_now": bind_now}


@case("symbols_include_dynsym_when_stripped")
def _t4():
    path = pick("/bin/ls", "/usr/bin/ls")
    e = _elf.load(path)
    syms = e.symbols()
    out = readelf("--dyn-syms", "-W", path)
    # a readelf symbol line is "N: addr size TYPE BIND VIS Ndx NAME[@VER] [(n)]",
    # so the name is the 8th field -- anchoring on end-of-line instead caught
    # only the four symbols that happen to carry no version suffix
    names = set()
    for line in out.splitlines():
        f = line.split()
        if len(f) >= 8 and f[0].endswith(":"):
            names.add(f[7].split("@")[0])
    common = names & syms
    assert len(common) > 10, "only %d dynsym names recovered: %r" % (
        len(common), sorted(common)[:5])
    return {"parsed": len(syms), "overlap_with_readelf": len(common)}


@case("libc_has_every_essential_gadget")
def _t5():
    path = pick("/usr/lib/x86_64-linux-gnu/libc.so.6", "/lib/x86_64-linux-gnu/libc.so.6")
    e = _elf.load(path)
    s = _gad.summary(e)
    assert not s["missing_essential"], "libc is missing %r, so the byte-pattern " \
        "search is broken rather than the libc" % s["missing_essential"]
    for text, addrs in s["present"].items():
        a = int(addrs[0], 16)
        off = next((o + (a - v) for o, v, n in _gad.exec_ranges(e) if v <= a < v + n), None)
        assert off is not None, "%s at %s is outside every executable segment" % (text, addrs[0])
        pat = next(p for p, t in _gad.PATTERNS.items() if t == text)
        assert e.data[off:off + len(pat)] == pat, \
            "%s at %s does not actually contain %s" % (text, addrs[0], pat.hex())
    return {"gadgets": {k: v[0] for k, v in s["present"].items()}}


@case("non_elf_is_refused_not_guessed")
def _t6():
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as fh:
        fh.write(b"this is not an ELF file at all\n")
        name = fh.name
    try:
        try:
            _elf.load(name)
        except _elf.NotAnELF:
            return {"refused": True}
        raise AssertionError("a text file was parsed as an ELF")
    finally:
        os.unlink(name)


@case("triage_cli_runs_and_emits_json")
def _t7():
    path = pick("/bin/ls", "/usr/bin/ls")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cli = os.path.join(root, "pwn_triage.py")
    r = subprocess.run([sys.executable, cli, path], capture_output=True,
                       text=True, timeout=60)
    assert r.returncode == 0, "exit %d: %s" % (r.returncode, r.stderr[:300])
    doc = json.loads(r.stdout)
    for key in ("protections", "dangerous_symbols", "gadgets",
                "routes_still_open", "offset_without_gdb", "evidence_note"):
        assert key in doc, "missing key %r" % key
    assert doc["routes_still_open"], "no route proposed at all"
    return {"keys": len(doc), "routes": len(doc["routes_still_open"])}


@case("no_absent_dependency_is_imported")
def _t8():
    root = os.path.dirname(os.path.abspath(__file__))
    # "pwn" stays on this list: the package is named pwnstatic exactly so that
    # it cannot shadow pwntools' own top-level "pwn" module once that is installed
    banned = ("pwn", "pwnlib", "gdb", "z3", "gmpy2", "fpylll", "angr",
              "unicorn", "keystone", "ropper", "elftools")
    bad = []
    for fn in sorted(os.listdir(root)) + [os.path.join("..", "pwn_triage.py")]:
        if not fn.endswith(".py"):
            continue
        with open(os.path.join(root, fn)) as fh:
            for i, line in enumerate(fh, 1):
                s = line.strip()
                if not (s.startswith("import ") or s.startswith("from ")):
                    continue
                mod = s.split()[1].split(".")[0]
                if mod in banned and "capstone" not in s:
                    bad.append("%s:%d %s" % (fn, i, s))
    assert not bad, "absent dependency imported at module level: %r" % bad
    return {"files_checked": len([f for f in os.listdir(root) if f.endswith(".py")]) + 1,
            "banned_imports": 0}


@case("static_canary_symbol_is_not_asserted_as_a_canary")
def _t9():
    """The false positive that would cost a leak nobody needed.

    A binary built with -fno-stack-protector and -static still carries
    __stack_chk_fail, because static glibc brings its own. Measured on this
    machine: main() has zero %fs:0x28 loads while the symbol is present.
    """
    import shutil
    import tempfile
    if not shutil.which("gcc") or not shutil.which("objdump"):
        raise SkipTest("gcc or objdump absent; the caveat cannot be re-measured")
    src = "int main(void){ char b[64]; return __builtin_snprintf(b,64,\"x\"); }"
    d = tempfile.mkdtemp()
    try:
        c, out = os.path.join(d, "t.c"), os.path.join(d, "t")
        with open(c, "w") as fh:
            fh.write(src)
        r = subprocess.run(["gcc", "-static", "-fno-stack-protector", "-o", out, c],
                           capture_output=True, text=True, timeout=180)
        if r.returncode != 0:
            raise SkipTest("no static libc to link against: " + r.stderr[-160:])
        prot = _prot.protections(_elf.load(out))
        assert prot["static"]["value"], "the -static build has a PT_INTERP"
        if not prot["canary"]["value"]:
            raise SkipTest("this libc carries no __stack_chk_fail, so the false "
                           "positive cannot occur here")
        assert prot["canary"]["trustworthy"] is False, \
            "a static binary's libc canary symbol was reported as trustworthy"
        dis = subprocess.run(["objdump", "-d", "--no-show-raw-insn", out],
                             capture_output=True, text=True, timeout=120).stdout
        body, seen = [], False
        for line in dis.splitlines():
            if "<main>:" in line:
                seen = True
                continue
            if seen and line.strip().endswith(">:"):
                break
            if seen:
                body.append(line)
        real = sum(1 for line in body if "fs:0x28" in line)
        assert real == 0, "main has %d %%fs:0x28 loads, so -fno-stack-protector " \
            "did not apply and this case proves nothing" % real
        return {"symbol_present": True, "trustworthy": False,
                "fs_0x28_loads_in_main": real}
    finally:
        import shutil as _sh
        _sh.rmtree(d, ignore_errors=True)


def main():
    width = max(len(n) for _, n, _ in RESULTS)
    for status, name, detail in RESULTS:
        print("%-4s %-*s %s" % (status, width, name,
                                json.dumps(detail, default=str)
                                if not isinstance(detail, str) else detail))
    bad = sum(1 for s, _, _ in RESULTS if s == "FAIL")
    print("\n%d pass, %d skip, %d FAIL" % (
        sum(1 for s, _, _ in RESULTS if s == "PASS"),
        sum(1 for s, _, _ in RESULTS if s == "SKIP"), bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
