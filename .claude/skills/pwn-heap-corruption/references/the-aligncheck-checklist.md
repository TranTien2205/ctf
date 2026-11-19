# Alignment checks — where they catch you — checklist

Companion to `the-aligncheck.md`.

## Checklist

- [ ] The pointer passed to free must be chunk_addr + 0x10 (the user area)
- [ ] Aiming a bin at a misaligned target: the return is still aligned
