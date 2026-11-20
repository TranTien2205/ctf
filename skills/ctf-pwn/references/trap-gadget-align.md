# Trap: alignment crashes

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

movaps on an unaligned stack segfaults silently mid-chain - the 'worked locally' crash on Ubuntu is usually one missing ret gadget for 16-byte alignment.

## Pivot

Module read -> the technique file or class skill it names.
