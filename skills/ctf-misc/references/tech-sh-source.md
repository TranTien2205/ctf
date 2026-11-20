# Technique: Source/. escape

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

The `.` builtin reads a file as commands - a file you control (or /etc/profile-ish paths) becomes your payload when `source` survives.

## Evidence rule

The technique claim still needs the verbatim output - a technique
name is routing information, not a finding.

## Pivot

Technique identified -> the shared file carrying its detail.
