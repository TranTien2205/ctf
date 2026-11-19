# Gadget side effects — the hidden costs — checklist

Companion to `the-side-effects.md`.

## Checklist

- [ ] extra pops (consumes extra qwords — the chain must provide them).
- [ ] memory writes (clobbers a region).
- [ ] conditional jumps (control may not reach the ret).
