# Attack: Coppersmith small roots

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Partial knowledge of p or of m (MSB known) -> LLL-based small-root recovery - bound is a fraction of n's bits.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
