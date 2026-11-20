# Partial overwrite

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Low-byte writes defeat ASLR on the same page: overwrite 1-2 bytes of a pointer to retarget within +/- 64KB; carries no leak requirement.

## Pivot

Module read -> the technique file or class skill it names.
