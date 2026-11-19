# Verifying the call target — before the chain — checklist

Companion to `the-call-target-check.md`.

## Checklist

- [ ] system: needs a string arg — the "/bin/sh" question.
- [ ] a win func: verify it actually reads the flag (disassemble it).
- [ ] a PLT import: confirm the import exists (afl / nm).
