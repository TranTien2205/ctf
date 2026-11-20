# libc questions

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Which libc (supplied vs remote) decides symbol resolution: file magic + strings + the GOT-resolved addresses; a mismatched libc turns a correct chain into a crash - the libc fingerprint modules in the class skills carry the offset checks.

## Pivot

Module read -> the shared file or class skill it names.
