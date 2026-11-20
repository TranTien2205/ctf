# Attack: LFSR from keystream

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

2L keystream bits -> Berlekamp-Massey -> the polynomial -> predict; nonlinear combos need the correlation attack per constituent.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
