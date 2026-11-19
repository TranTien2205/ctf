# False signals — the traps — checklist

Companion to `the-false-signal.md`.

## Checklist

- [ ] A `pop rdi` that isn't: the disassembly's byte-alignment — verify
- [ ] A leak value that ISN'T a pointer: read the wrong field.
- [ ] A win function that prints a decoy: disassemble before chaining.
- [ ] A clean exit: not success — the observable must fire.
