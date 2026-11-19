# malloc_printerr — the abort path — checklist

Companion to `the-malloc-printerr.md`.

## Checklist

- [ ] The abort itself uses stdio — a corrupted stderr FILE fires DURING
- [ ] Reading the abort text names the failed check — your diagnostic.
