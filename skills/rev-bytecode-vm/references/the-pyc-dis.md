# pyc_dis.py — the tool's path


The local tool does the marshal+dis walk:

    python3 tools/pyc_dis.py file.pyc            # full dis listing
    python3 tools/pyc_dis.py file.pyc --strings  # constants/names only
    python3 tools/pyc_dis.py --selftest

## The --strings route

Fastest triage: constants + names only — flag-shaped constants and
interesting names jump out before reading bytecode.
