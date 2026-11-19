# The probe budget — the bytecode route — checklist

Companion to `the-budget.md`.

## Checklist

- [ ] pyc_dis --strings: one probe, fast.
- [ ] dis walk + inversion: a few minutes.
- [ ] Custom VM table recovery: the bulk of the budget.
- [ ] Trace fallback: only after static fails.
