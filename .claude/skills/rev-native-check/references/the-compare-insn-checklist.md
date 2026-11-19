# cmp instruction forms — the operand types — checklist

Companion to `the-compare-insn.md`.

## Checklist

- [ ] cmp rax, 0x41 — vs immediate.
- [ ] cmp rax, rbx — vs register.
- [ ] cmp rax, [rbp-8] — vs memory.
- [ ] cmp byte [rdi], al — a byte at a pointer.
- [ ] cmp dword [rax], 0xdead — a sized memory compare.
