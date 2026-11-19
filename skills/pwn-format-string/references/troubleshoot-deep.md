# Troubleshooting — symptom → cause → fix — deep

Companion to `troubleshoot.md`.

The format string is an argument-position interpreter: %p/%x read, %s derefs, %n writes the cumulative count. Every specifier is index-addressed — locate N, steer the count, choose the target.

## Boundary conditions

- x64: args 1-6 in registers; stack args N≥6.
- A literal format closes the class.
- Full RELRO closes GOT.
- glibc ≥2.35 removes the hooks.
- %s/%n reads/writes until a \x00.
