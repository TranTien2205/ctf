# Hunting pop rdx — the scarce arg — checklist

Companion to `the-pop-rdx-hunt.md`.

## Checklist

- [ ] `pop rdx; pop rXX; ret` — a paired pop.
- [ ] `xor edx, edx` gadgets — for a 0 arg.
- [ ] ret2csu's `mov rdx, r15` path.
- [ ] A `mov rdx, rXX` gadget when a register holds the value.
