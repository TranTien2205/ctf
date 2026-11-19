# The index-as-pointer bug — confusion — checklist

Companion to `the-index-bug.md`.

## Checklist

- [ ] 1. Object A holds an index/id field the lookup uses.
- [ ] 2. Overlap corrupts the index field.
- [ ] 3. The next lookup on A reads a different slot's pointer — confusion
