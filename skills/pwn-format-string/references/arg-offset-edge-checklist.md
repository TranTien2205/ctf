# Arg-offset edge cases — when AAAA.%N$p misleads — checklist

Companion to `arg-offset-edge.md`.

## Checklist

- [ ] 1. Use a longer marker: 'AAAABBBB' → look for the 8-byte value.
- [ ] 2. Your input may appear at multiple positions — test each for
- [ ] 3. 'AAAA' could align across two args — check adjacent N.
