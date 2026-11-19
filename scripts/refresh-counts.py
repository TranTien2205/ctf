#!/usr/bin/env python3
"""Write the suite's own test count into the documents that claim it.

WHY THIS EXISTS, measured: the doc count went stale five times in one
session. Every time the cause was the same - the count was taken by a
separate `pytest --collect-only` call, then tests were added, and the gate
then failed on `doc pytest count matches collection`. Each failure cost a
full gate run, and each fix was the same two `sed` commands typed again.

A habit that fails five times is a mechanism that does not exist. So the
measurement and the write happen here, in one step, and `selftest.py` still
checks the result independently - this script does not get to assert that
it worked.

    python scripts/refresh-counts.py          # measure, write, report
    python scripts/refresh-counts.py --check  # report only, exit 1 if stale

Standard library only, like the rest of the package: an engagement should
not fail on a pip install.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: Each document and the pattern whose one capture group is the count.
#: A document that claims the number has to be here, or the gate will
#: eventually disagree with it and nobody will know which is right.
CLAIMS = (
    ("docs/VERIFICATION.md", r"# (\d+) unit \+ live-lab \+ loop tests"),
    ("CHANGELOG.md", r"`python -m pytest tests/ -q`: (\d+) tests"),
)


def collected() -> int:
    """How many tests the suite collects, from pytest itself.

    `--collect-only -q` prints "N tests collected" as its last line. Read
    that rather than counting `def test_` in the files: parametrised cases
    are tests and a source count is not the number the gate compares
    against.
    """
    out = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--collect-only"],
        cwd=ROOT, capture_output=True, text=True, timeout=900)
    found = re.findall(r"(\d+) tests? collected", out.stdout)
    if not found:
        raise SystemExit("pytest did not report a collection count:\n"
                         + (out.stdout or out.stderr)[-400:])
    return int(found[-1])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="report staleness and exit 1, writing nothing")
    args = ap.parse_args()

    n = collected()
    print(f"collected: {n}")
    stale = []
    for rel, pattern in CLAIMS:
        path = ROOT / rel
        if not path.is_file():
            print(f"  {rel}: missing")
            continue
        text = path.read_text(encoding="utf-8")
        found = re.search(pattern, text)
        if found is None:
            # A document that stopped claiming the count is not an error -
            # but it is not silently fine either, because the gate's check
            # is keyed on the same shape and would stop covering it.
            print(f"  {rel}: no count claim matching {pattern!r}")
            continue
        was = int(found.group(1))
        if was == n:
            print(f"  {rel}: {was} (current)")
            continue
        stale.append(f"{rel}: {was} -> {n}")
        if args.check:
            print(f"  {rel}: {was}, STALE (collection finds {n})")
            continue
        path.write_text(
            text[:found.start(1)] + str(n) + text[found.end(1):],
            encoding="utf-8")
        print(f"  {rel}: {was} -> {n}")

    if args.check and stale:
        print("stale: " + "; ".join(stale))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
