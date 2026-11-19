# jmp/call endings — non-ret gadgets — checklist

Companion to `the-jmp-end.md`.

## Checklist

- [ ] `jmp rax` with rax = your next gadget — the chain is a jump-table.
- [ ] `call [reg]` — the call's return address is pushed — the gadget's
