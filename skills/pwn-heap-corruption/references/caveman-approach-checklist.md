# The caveman order — cheap techniques first — checklist

Companion to `caveman-approach.md`.

## Checklist

- [ ] 1. unsorted-bin leak (free + read) — the cheapest, always first.
- [ ] 2. tcache poisoning — one write.
- [ ] 3. fastbin dup — three frees.
- [ ] 4. size corruption → consolidate overlap.
- [ ] 5. house-of-* — the big setups.
- [ ] 6. FSOP — when hooks are gone.
