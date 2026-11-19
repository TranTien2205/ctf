# stack-protector-strong vs -all — which functions get canaries — checklist

Companion to `stack-protector-strong.md`.

## Checklist

- [ ] gcc's -fstack-protector only guards functions with vulnerable arrays;
- [ ] strong adds address-taken locals; -all guards everything. The canary
- [ ] presence is PER-FUNCTION, not per-binary.
- [ ] Observation | Meaning
- [ ] the vuln function has no %fs:0x28 load | this function is unprotected
- [ ] a different function has it | per-function protection
- [ ] the binary 'has' __stack_chk_fail | imported, maybe unused here
- [ ] Disassemble THE vulnerable function — its own prologue/epilogue shows
- [ ] whether IT is protected, not whether the binary imports the symbol.
- [ ] The vulnerable function has no canary even though the binary 'uses'
- [ ] stack-protector — the smash in it succeeds.
