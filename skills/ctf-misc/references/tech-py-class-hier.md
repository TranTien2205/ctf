# Technique: PyJail class hierarchy

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

().__class__.__mro__ and __subclasses__ on any object reach the whole hierarchy - warnings.catch_warnings, os._wrap_close and co. are the usual reachable leaves.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
