# Attack: Franklin-Reiter related

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Two ciphertexts of LINEARLY related plaintexts under same n -> gcd of polynomials recovers m - tools/crypto/franklin_reiter.py --selftest exists.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
