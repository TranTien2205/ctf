# The .wasm check — reading the verification function — checklist

Companion to `wasm-check-depth.md`.

## Checklist

- [ ] local.get/global.get: load a value
- [ ] i32.const: push a constant
- [ ] i32.xor/i32.add/i32.eq/i32.eqz: the ops
- [ ] call: a helper
- [ ] br_if/if: the branch
- [ ] i32.load8_u: read a byte from memory
