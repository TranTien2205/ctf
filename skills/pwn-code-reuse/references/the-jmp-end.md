# jmp/call endings — non-ret gadgets


A gadget ending in `jmp reg` or `call reg` transfers control — the
chain continues only if the register points at the next stage.

## The rule

- `jmp rax` with rax = your next gadget — the chain is a jump-table.
- `call [reg]` — the call's return address is pushed — the gadget's
  continuation differs.

## Falsifier

The transfer goes somewhere you can't predict — prefer ret-terminated
gadgets.
