# Trap: RELRO half-read

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Partial RELRO leaves .got writable but .got.plt resolution lazy - overwrite candidates differ from full/no RELRO; the triage output names which GOT fields are open.

## Pivot

Module read -> the shared file or class skill it names.
