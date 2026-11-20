# Technique: PyJail getattr construction

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

getattr(obj, '_'*5+'class_'...) builds the attr name from pieces when literal names are filtered - chr() joins supply the banned letters.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
