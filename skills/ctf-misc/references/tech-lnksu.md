# Technique: Symlink/exec trick

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

If the jail filters commands by name, a symlink to a binary under a different name can pass - the filter checks the name not the inode.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
