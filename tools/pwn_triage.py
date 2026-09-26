#!/usr/bin/env python3
"""First contact with a pwn binary: protections, imports, gadgets, routes left.

Why this exists rather than a pwntools one-liner: pwntools, gdb, ROPgadget,
ropper, one_gadget, checksec and patchelf are all measured ABSENT on this
machine, and pip here is EXTERNALLY-MANAGED, so during a contest the import
fails and the minutes go to fixing the toolchain. This is standard library only,
like tools/crypto/, and answers the questions that decide the first hour.

    python3 tools/pwn_triage.py ./chal
    python3 tools/pwn_triage.py ./chal --gadgets          # the full gadget list
    python3 tools/pwn_triage.py ./chal --challenge name   # emit a ledger probe

It reports and it ranks; it does not claim a bug. The routes it prints are
hypotheses in the AGENTS.md sense and carry no evidentiary weight until a probe
against the real binary produces a captured result.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pwnstatic import elf as _elf              # noqa: E402
from pwnstatic import gadgets as _gad          # noqa: E402
from pwnstatic import protections as _prot     # noqa: E402

ABSENT = ["pwntools", "gdb", "ROPgadget", "ropper", "one_gadget", "checksec", "patchelf"]


def offset_hint(prot):
    """How to get the overflow offset with no gdb on this machine."""
    if prot["static"]["value"]:
        return ("no gdb here: find the offset by feeding a cyclic pattern on stdin "
                "and reading the faulting address out of the core file "
                "(`ulimit -c unlimited`, then `readelf -n core` or "
                "`strings -a core`), or bisect the length until the crash moves")
    return ("no gdb here: bisect the input length until SIGSEGV appears, then "
            "confirm the offset by overwriting the return address with a known "
            "8-byte marker and checking the faulting address in dmesg "
            "(`dmesg | tail`) or a core file")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("binary")
    ap.add_argument("--gadgets", action="store_true",
                    help="list every matched gadget, not just the essential set")
    ap.add_argument("--challenge", help="also print the probe command to record "
                                        "this triage in that challenge's ledger")
    a = ap.parse_args()

    if not os.path.isfile(a.binary):
        print(json.dumps({"error": "not a file", "path": a.binary}), file=sys.stderr)
        return 2
    try:
        e = _elf.load(a.binary)
    except _elf.NotAnELF as exc:
        print(json.dumps({
            "error": "not an ELF: %s" % exc,
            "path": a.binary,
            "hint": "check `file` and `binwalk`; a .pyc, a Mach-O, a PE or an "
                    "archive needs a different tool, and this one refuses rather "
                    "than guessing",
        }, indent=2))
        return 2

    prot = _prot.protections(e)
    dang = _prot.dangerous(e)
    report = {
        "binary": os.path.abspath(a.binary),
        "size": os.path.getsize(a.binary),
        "protections": prot,
        "dangerous_symbols": dang,
        "gadgets": _gad.find(e) if a.gadgets else _gad.summary(e),
        "routes_still_open": _prot.leads(prot, dang),
        "offset_without_gdb": offset_hint(prot),
        "tools_absent_on_this_machine": ABSENT,
        "evidence_note": "reader output: every field above is read from the file "
                         "on disk. routes_still_open is hypothesizer output and "
                         "confirms nothing until a probe runs.",
    }
    if a.challenge:
        report["record_this"] = (
            "python3 tools/hooks.py post-probe %s --hypothesis-id h1 "
            "--class pwn-triage --verdict inconclusive --evidence-kind class "
            "--evidence 'nx=%s pie=%s relro=%s canary=%s' "
            "# triage is recon, never a confirm" % (
                a.challenge, prot["nx"]["value"], prot["pie"]["value"],
                prot["relro"]["value"], prot["canary"]["value"]))
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
