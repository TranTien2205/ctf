# Endianness and register width — x86 vs x64 — case catalogue

x86 (32-bit) args go on the stack; x64 args go in rdi/rsi/rdx. Pattern chunks and addresses are 4 vs 8 bytes. Get the width right or the chain is garbage.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | ELF class: ELF64 | x64 | rdi/rsi/rdx pops |
| 2 | ELF class: ELF32 | x86 | args on stack |
| 3 | 32-bit cyclic --find | 4-byte offsets | same for both |

## Falsifier

Falsifier — you built an x64-style chain on a 32-bit binary (or vice versa): the arg placement is wrong; rebuild.
