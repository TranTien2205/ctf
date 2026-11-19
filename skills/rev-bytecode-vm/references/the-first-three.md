# The first three probes — the bytecode order

1. `python3 tools/pyc_dis.py f.pyc --strings` — constants scan.
2. `python3 tools/pyc_dis.py f.pyc` — full dis of the check.
3. Invert the transform → produce the input.

For a custom VM: (1) locate dispatch, (2) recover table, (3) decode
program.
