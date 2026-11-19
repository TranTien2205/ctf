# Locating the check in a .pyc — deep

Companion to `pyc-check-locate.md`.

--strings for names (check/verify) + flag-shaped consts → dis only that code object → find the COMPARE_OP → read its operands.
