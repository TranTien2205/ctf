# Attack: LCG from outputs

Depth module for `ctf-crypto`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

x[i+1] = a*x[i]+c mod m: three outputs with known m -> a,c linear; unknown m -> differences' gcd - the tool exists.

## Evidence rule

The attack claim needs its precondition measured and its output
verified - 'applied X' without the recovered value is a candidate.

## Pivot

Attack spent -> the precondition that would reopen it, or the next
family per the triage.
