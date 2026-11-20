# Trap: libc version mismatch

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Correct chain, wrong libc = crash. Fingerprint via leaked symbol low-bytes against the supplied libc's symbol table - the offset delta names the version before the chain runs.

## Pivot

Module read -> the shared file or class skill it names.
