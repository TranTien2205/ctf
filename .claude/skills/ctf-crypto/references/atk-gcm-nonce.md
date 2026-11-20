# Attack: GCM nonce misuse

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Nonce reuse leaks the GHASH authentication key -> forgery after two same-nonce ciphertexts - the algebraic recovery is in modern-ciphers files.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
