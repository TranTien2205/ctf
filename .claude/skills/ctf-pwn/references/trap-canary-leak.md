# Trap: canary assumptions

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

A canary is per-process random - leaking it once and reusing across runs fails; the leak must be in the SAME connection/process as the smash.

## Pivot

Module read -> the shared file or class skill it names.
