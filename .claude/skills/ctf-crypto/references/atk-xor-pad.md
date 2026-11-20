# Attack: Multi-time pad crib-drag

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Keystream reuse across messages: XOR pairs, crib-drag with likely words ('flag{', 'the ', spaces) - the space-vs-letter XOR signature is the wedge.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
