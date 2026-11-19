# More side effects — the subtle ones — checklist

Companion to `the-side-effects-2.md`.

## Checklist

- [ ] A gadget that pops N registers consumes N qwords — the chain must
- [ ] A `push`-containing gadget writes to the stack below rsp — usually
- [ ] A conditional branch inside the gadget may skip the ret entirely.
