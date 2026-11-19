# Detection — naming this class

## Fire

- A .pyc, .class, .wasm, .beam, .dex, .pyc-embedded-in-exe.
- A binary with a fetch-decode-execute dispatch loop over a byte
  program.
- A serialized code object (marshal).

## Boundary cases

- A .pyc that imports a compiled .so — the check may be in the .so
  (native), not the bytecode.
- A minified script — text, not bytecode (boundary thin).
- A VM inside a VM — nested; each layer's table recovered
  separately.
