# Detection — naming this class — checklist

Companion to `detection-deep.md`.

## Checklist

- [ ] A .pyc, .class, .wasm, .beam, .dex, .pyc-embedded-in-exe.
- [ ] A binary with a fetch-decode-execute dispatch loop over a byte
- [ ] A serialized code object (marshal).
- [ ] A .pyc that imports a compiled .so — the check may be in the .so
- [ ] A minified script — text, not bytecode (boundary thin).
- [ ] A VM inside a VM — nested; each layer's table recovered
