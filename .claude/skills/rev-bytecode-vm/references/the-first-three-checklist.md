# The first three probes — the bytecode order — checklist

Companion to `the-first-three.md`.

## Checklist

- [ ] 1. `python3 tools/pyc_dis.py f.pyc --strings` — constants scan.
- [ ] 2. `python3 tools/pyc_dis.py f.pyc` — full dis of the check.
- [ ] 3. Invert the transform → produce the input.
