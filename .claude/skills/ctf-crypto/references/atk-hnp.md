# Attack: HNP biased nonces

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Partially-known nonce bits per signature -> hidden number problem -> lattice row recovery; needs several signatures - lattice-and-lwe.md carries the setup.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
