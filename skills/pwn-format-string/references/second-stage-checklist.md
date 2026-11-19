# Two-stage — leak then write — checklist

Companion to `second-stage.md`.

## Checklist

- [ ] 1. Stage 1: %p run or %s read → canary, base, the target's address.
- [ ] 2. Stage 2: %n write → GOT/ret-addr/hook overwritten with the chain.
