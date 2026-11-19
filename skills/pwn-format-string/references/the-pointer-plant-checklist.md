# Planting the pointer — getting your address into a %N position — checklist

Companion to `the-pointer-plant.md`.

## Checklist

- [ ] Your input bytes land as an argument — a pointer written as raw bytes
- [ ] AAAA.<addr-as-8-bytes>.%N$s — the addr is in your input, %N$s derefs it.
- [ ] The addr must be at the right argument position — the arg-offset-finder.
