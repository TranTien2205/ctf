# The glibc version question — before any technique


Every heap technique is version-keyed: a recipe written for glibc 2.27
dies silently on 2.36. Answer the version question before choosing
anything.

## Ways to answer it

- The challenge ships a libc — `strings libc.so.6 | grep -i 'glibc'`.
- A stated base image (ubuntu:20.04 → 2.31; 18.04 → 2.27; 22.04 → 2.35).
- A leaked libc pointer → match known symbol offsets.
- `ldd --version` on the matching toolchain (coarse check).

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

No way to determine the libc: state the unknown and pick the technique
family that is version-tolerant first (leaks before writes).
