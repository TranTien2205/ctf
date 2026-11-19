# Allocation poisoning — what the next alloc sees — checklist

Companion to `allocation-poison.md`.

## Checklist

- [ ] The alloc's return = your target → aim confirmed.
- [ ] The alloc's content = the target's bytes → a read primitive.
- [ ] A write into it = the payload landing.
