# Technique: PyJail via exceptions

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Exception handlers see the raised object - raising a crafted exception inside a filtered eval reaches __context__/__cause__ attribute chains.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
