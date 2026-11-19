# The csu fields — what each reg does — checklist

Companion to `the-csu-fields.md`.

## Checklist

- [ ] rbx: the call's index (0 for one call).
- [ ] rbp: the loop bound (rbx+1 → 1).
- [ ] r12 + rbx*8: the call target's address (a pointer TO the func).
- [ ] r13d → edi: arg0.
- [ ] r14 → rsi: arg1.
- [ ] r15 → rdx: arg2.
