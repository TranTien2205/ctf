# Constant strings in a .pyc

The co_consts table holds every string literal — the check's expected value, the flag format, the error strings. `pyc_dis.py --strings` lists them; a flag-shaped constant is a candidate, verify it.

## The route

Locate the check, read the transform, extract the expected, produce the input, verify on the real interpreter. See `the-workflow.md` and `evidence-depth.md`.
