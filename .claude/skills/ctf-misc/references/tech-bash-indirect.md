# Technique: Bash indirect expansion

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

${!var} dereferences a name held in a variable - x='PATH'; ${!x} yields PATH's value; chained indirection builds command names.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
