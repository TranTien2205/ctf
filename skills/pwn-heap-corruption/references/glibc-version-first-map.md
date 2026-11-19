# The glibc version question — before any technique — map

Companion to `glibc-version-first.md`.

## Ways to answer it
## Version-anchored facts
| glibc | Consequence |
|---|---|
| 2.26 | tcache introduced — freed chunks hit the per-thread bin first |
| 2.29 | tcache key/count checks — naive double-free detected |
| 2.30 | unlink hardening — classic unlink dead |
| 2.31 | tcache-aligned counts, more checks |
| 2.32 | safe-linking — fd pointers are mangled, need a leak to aim |
| 2.34 | __free_hook/__malloc_hook removed |
| 2.35 | tcache key further hardened in practice |
## Falsifier
