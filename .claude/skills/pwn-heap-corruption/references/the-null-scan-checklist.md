# Reading a null result — when the leak reads 0 — checklist

Companion to `the-null-scan.md`.

## Checklist

- [ ] Try a different freed chunk — a mid-bin one has live fd.
- [ ] A bin-tail fd=0 is itself information: the chunk was last freed.
