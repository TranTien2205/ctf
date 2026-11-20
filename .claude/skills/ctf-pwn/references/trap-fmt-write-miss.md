# Trap: %n on the wrong width

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

%hn/%hhn/%n widths change the write granularity AND the printed-count requirement; a wrong-width write corrupts adjacent bytes - the class skill's width table is the check.

## Pivot

Module read -> the shared file or class skill it names.
