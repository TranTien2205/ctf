# Chain verification — landing it step by step — checklist

Companion to `chain-verification.md`.

## Checklist

- [ ] Don't build the whole chain and test it once — verify each stage: does
- [ ] the first gadget execute? does the call site run? does the output appear?
- [ ] 1. The offset — cyclic + fault: RIP holds your bytes.
- [ ] 2. The first gadget — a ret/pop that runs.
- [ ] 3. The call site — the function/syscall executes (visible side-effect).
- [ ] 4. The output — the flag or the shell.
- [ ] Each stage's failure points at a specific boundary (alignment, arg,
- [ ] bad-byte) — fix the stage, don't rebuild the whole chain.
