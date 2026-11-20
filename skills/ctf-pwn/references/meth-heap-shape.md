# Heap exploitation shape

Depth module for `ctf-pwn`. Open `../SKILL.md` for the shared-file
index first; this file is one named piece of the corpus - never a
finding by itself.

Allocator version decides the primitives: tcache poison vs unsorted-bin leak vs house-of-X - heap-techniques*.md and heap-fsop.md carry the per-version shapes; the class skill carries the glibc version checks.

## Pivot

Module read -> the shared file or class skill it names.
