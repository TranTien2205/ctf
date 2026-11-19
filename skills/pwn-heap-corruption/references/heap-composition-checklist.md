# Composing heap with other classes — checklist

Companion to `heap-composition.md`.

## Checklist

- [ ] heap-leak → stack overflow: the leak's stack addr feeds the smash.
- [ ] fmtstr on a heap buffer: the %n write IS the heap corruption.
- [ ] heap → ROP: the write lands a ROP chain on a known stack/heap addr.
- [ ] heap → FSOP: a write inside libc's data.
