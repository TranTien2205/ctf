# Technique: PyJail import tricks

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

__import__('os') alternatives: importlib.import_module, __builtins__['__import__'], sys.modules grafting, __loader__ specs - each a different filter surface.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
