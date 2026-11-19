# Integrity checks by version — the gauntlet — checklist

Companion to `the-consistency-checks.md`.

## Checklist

- [ ] size alignment & minimum — always.
- [ ] next-size sanity on free — always.
- [ ] fastbin top double-free — early.
- [ ] tcache count bounds — 2.26+.
- [ ] tcache key — 2.29+.
- [ ] smallbin unlink fd<->bk consistency — 2.30+.
- [ ] corrupted top size — 2.29+.
- [ ] safe-linking (mangled fd) — 2.32+.
- [ ] large-bin size ordering checks — 2.30+.
