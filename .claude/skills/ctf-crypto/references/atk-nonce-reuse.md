# Attack: ECDSA nonce reuse

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Same r in two signatures -> k = (h1-h2)/(s1-s2) mod n -> private key from k - the r-pair is the precondition.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
