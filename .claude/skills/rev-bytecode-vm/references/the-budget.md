# The probe budget — the bytecode route

- pyc_dis --strings: one probe, fast.
- dis walk + inversion: a few minutes.
- Custom VM table recovery: the bulk of the budget.
- Trace fallback: only after static fails.

Don't re-derive the table — decode the program against it once.
