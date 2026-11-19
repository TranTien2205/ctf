# Endianness and register width — x86 vs x64

x86 (32-bit) args go on the stack; x64 args go in rdi/rsi/rdx. Pattern chunks and addresses are 4 vs 8 bytes. Get the width right or the chain is garbage.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| ELF class: ELF64 | x64 | rdi/rsi/rdx pops |
| ELF class: ELF32 | x86 | args on stack |
| 32-bit cyclic --find | 4-byte offsets | same for both |

## Steps

1. readelf -h ./chal | grep Class — ELF32 vs ELF64.
2. x64 chain: pop rdi;ret + arg + pop rsi;ret + arg + call.
3. x86 chain: call + ret-to + arg1 + arg2 (args ON the stack).
4. Pattern --find takes 4 bytes in both cases.

## Falsifier

Falsifier — you built an x64-style chain on a 32-bit binary (or vice versa): the arg placement is wrong; rebuild.

## Traps

- On x86, 'pop rdi' doesn't exist — args literally go on the stack.
- Return address is 4 bytes on x86, 8 on x64 — the padding differs.

## Commands

```bash
readelf -h ./chal | grep Class
```

## Cross-references

`boundary-cases.md` · `rop-basics.md`
