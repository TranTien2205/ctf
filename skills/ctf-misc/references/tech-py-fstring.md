# Technique: PyJail f-string escape

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

f-strings evaluate expressions at format time - f'{x.__class__}' reaches attributes inside an otherwise filtered eval context.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
