# The saved-return write — a complete recipe — checklist

Companion to `fmtstr-ret-addr-full.md`.

## Checklist

- [ ] 1. Leak a stack pointer (saved rbp / argv) — compute the saved-ret slot.
- [ ] 2. saved_ret = *saved_rbp + 8 typically (verify the frame layout).
- [ ] 3. Plant the saved-ret address at arg position N (input bytes or a
- [ ] 4. %Nc ... %N$hn writes the target's bytes over saved_ret.
- [ ] 5. Function returns — redirect fires.
