# Canary bypass shapes

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Leak it (fmt read of the stack slot), or smash an unprotected path (thread-local, early-return paths), or brute-force on forking servers (byte-at-a-time, 256 requests worst-case per byte).

## Pivot

Module read -> the technique file or class skill it names.
