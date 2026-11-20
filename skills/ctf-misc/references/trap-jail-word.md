# Trap: word vs char filters

Depth module for `ctf-misc`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

A blocked WORD differs from a blocked CHAR: 'eval' blocked as a word still passes as 'ev''+'al'; a blocked char needs construction or encoding escapes, not concatenation.

## Pivot

Module read -> the shared file or class skill it names.
