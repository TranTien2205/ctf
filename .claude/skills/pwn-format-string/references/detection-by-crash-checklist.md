# Detection by crash — the %s crash oracle — checklist

Companion to `detection-by-crash.md`.

## Checklist

- [ ] %s at a bad addr crashes → the deref ran → the primitive exists.
- [ ] %s at a good addr doesn't → the addr valid → a 1-bit read.
- [ ] The crash signature confirms the primitive even without output.
- [ ] 1. Send %s at a controlled position; a crash = the deref ran.
- [ ] 2. A clean return = the planted address was valid.
- [ ] 3. The crash-or-clean oracle reads 1 bit per attempt.
