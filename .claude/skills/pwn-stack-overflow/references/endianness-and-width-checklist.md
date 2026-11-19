# Endianness and register width — x86 vs x64 — checklist

x86 (32-bit) args go on the stack; x64 args go in rdi/rsi/rdx. Pattern chunks and addresses are 4 vs 8 bytes. Get the width right or the chain is garbage.

## Checklist

- [ ] readelf -h ./chal | grep Class — ELF32 vs ELF64.
- [ ] x64 chain: pop rdi;ret + arg + pop rsi;ret + arg + call.
- [ ] x86 chain: call + ret-to + arg1 + arg2 (args ON the stack).
- [ ] Pattern --find takes 4 bytes in both cases.

## Abort conditions

- On x86, 'pop rdi' doesn't exist — args literally go on the stack.
- Return address is 4 bytes on x86, 8 on x64 — the padding differs.

## Falsifier

Falsifier — you built an x64-style chain on a 32-bit binary (or vice versa): the arg placement is wrong; rebuild.
