# Side effects in gadgets — the audit list — checklist

Companion to `the-side-effects-rop.md`.

## Checklist

- [ ] extra pops: consume extra qwords — budget them.
- [ ] memory writes: a `[reg]` store — ensure the target's harmless.
- [ ] calls: a mid-gadget call — its own stack use.
- [ ] conditional jumps: the condition must hold.
- [ ] register clobbers: an add/inc — don't set that reg earlier.
