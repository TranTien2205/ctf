# Remaining checks — the long tail — checklist

Companion to `the-remaining-checks.md`.

## Checklist

- [ ] calloc bypass path.
- [ ] mem2chunk arithmetic (ptr - 0x10).
- [ ] chunk2mem (chunk + 0x10).
- [ ] request2size rounding (the +0x18 & ~0xf on x64).
- [ ] checked_request2size (the overflow check).
- [ ] MAX_FASTBIN_SIZE.
- [ ] DEFAULT_TCACHE_COUNT (7).
- [ ] The tcache size-index formula (size>>4 - 2 x64).
