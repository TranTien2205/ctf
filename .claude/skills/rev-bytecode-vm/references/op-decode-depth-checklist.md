# Opcode decoding — reading a custom VM end-to-end — checklist

Companion to `op-decode-depth.md`.

## Checklist

- [ ] push_imm / push_reg: a constant or register onto the stack
- [ ] pop, dup, swap: stack manipulation
- [ ] add, sub, xor, and, or, shl, shr: arithmetic
- [ ] load_input / read_char: consume flag bytes
- [ ] cmp, test: compare stack top to expected
- [ ] jz, jnz, jmp, call, ret: control flow
- [ ] print / win / fail: the verdict
- [ ] Direct cmp: the expected bytes ARE the flag.
- [ ] Transformed cmp (xor/add/rol): invert the transform on the
- [ ] Hash/digest: see rev-native-check — can't invert, but can verify.
