# Register state at the crash — what the registers tell you — checklist

Companion to `register-state-at-crash.md`.

## Checklist

- [ ] The fault frame's registers are the evidence: RIP for control, the arg
- [ ] regs for what the call saw, RSP for where the stack points.
- [ ] RIP = pattern bytes → return control.
- [ ] rdi/rsi/rdx at the crash → what the call site was passing.
- [ ] RSP = pattern bytes → your data is where the stack points.
- [ ] A fault in the WRITE path → a write crash, not a return crash.
- [ ] ```bash
- [ ] r2 -d ./chal       # debug; dc to the crash; dr reads the registers
- [ ] ```
