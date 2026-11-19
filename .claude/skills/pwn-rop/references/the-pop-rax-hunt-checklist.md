# Hunting pop rax — the syscall number — checklist

Companion to `the-pop-rax-hunt.md`.

## Checklist

- [ ] `xor eax, eax; ...; add/inc eax` — building to the number.
- [ ] A `mov eax, ...` gadget.
- [ ] ret2csu doesn't help — rax isn't in its set.
