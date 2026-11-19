# RELRO and the GOT — the write question — checklist

Companion to `partial-vs-full-relro.md`.

## Checklist

- [ ] Partial RELRO: the GOT stays writable — GOT[x] can be overwritten to
- [ ] Full RELRO (BIND_NOW): the GOT is mapped read-only after init —
- [ ] Partial: GOT overwrite redirects an import's next call.
- [ ] Full: GOT is read-only — the chain must end at a call that goes
