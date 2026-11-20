# Technique: Bash arithmetic escape

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

$((...)) evaluates arithmetic without a subshell - $(($x)) where x='whoami' executes in some shells; also ${var:-default} and indirect expansion ${!var}.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
