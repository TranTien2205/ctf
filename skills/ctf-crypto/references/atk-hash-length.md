# Attack: Hash length extension

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

H(secret||m) with Merkle-Damgard (MD5/SHA1/SHA2-family) -> append ||pad||m' and continue the state - needs known H and secret LENGTH only.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
