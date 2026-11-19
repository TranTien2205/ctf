# calloc vs malloc — zeroing and path differences — checklist

Companion to `calloc-malloc-diff.md`.

## Checklist

- [ ] calloc: __libc_calloc → may bypass tcache (implementation/version
- [ ] calloc zeroes memory — sprayed data is clean.
- [ ] calloc(n, size) multiplies — integer overflow on n*size (older glibc)
- [ ] If the service callocs, freed chunks may not land in tcache where
- [ ] An integer-overflow calloc gives a small alloc with large semantic
