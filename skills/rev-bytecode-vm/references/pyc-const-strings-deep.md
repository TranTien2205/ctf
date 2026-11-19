# Constant strings in a .pyc — deep

Companion to `pyc-const-strings.md`.

The co_consts table holds every string literal — the check's expected value, the flag format, the error strings. `pyc_dis.py --strings` lists them; a flag-shaped constant is a candidate, verify it.
