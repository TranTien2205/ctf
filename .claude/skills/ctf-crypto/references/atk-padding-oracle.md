# Attack: CBC padding oracle

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Valid/invalid padding answer -> byte-at-a-time plaintext recovery ~256 queries per byte worst-case - the error alphabet measured first.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
