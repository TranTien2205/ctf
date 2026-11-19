# Endianness and register width — x86 vs x64 — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| ELF class: ELF64 | x64 | rdi/rsi/rdx pops |
| ELF class: ELF32 | x86 | args on stack |
| 32-bit cyclic --find | 4-byte offsets | same for both |

## Falsifier

Falsifier — you built an x64-style chain on a 32-bit binary (or vice versa): the arg placement is wrong; rebuild.
