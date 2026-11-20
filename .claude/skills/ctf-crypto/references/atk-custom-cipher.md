# Attack: Custom cipher audit

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Diff the construction against the standard it resembles - the break is usually the departure: missing rounds, weak key schedule, homebrew S-box, ECB under the hood.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
