# Technique: PyJail saved-object reach

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

sys.modules, sys.path_importer_cache, traceback frames, gc.get_objects() - pre-imported modules and live objects reach what the builtins lost.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
