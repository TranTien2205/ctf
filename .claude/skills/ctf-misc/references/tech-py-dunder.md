# Technique: PyJail dunder walk

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

().__class__.__base__.__subclasses__() climbs to object -> subclasses -> a class with __init__.__globals__ or a direct file/exec-capable one - pyjails.md carries the chains.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
