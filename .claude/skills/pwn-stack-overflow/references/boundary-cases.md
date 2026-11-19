# Boundary cases — where the textbook breaks

Each entry: the boundary, why the recipe breaks, the fix.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| 32-bit vs 64-bit | arg passing differs | x86 args on stack; x64 in regs |
| static vs dynamic | PLT/libc story differs | static = code in binary only |
| -fomit-frame-pointer | no saved RBP | leave;ret unavailable |
| tiny binary / few gadgets | chain construction hard | ret2csu or SROP or leak |

## Steps

1. 32-bit: args on the stack — chain is [func][ret][arg1][arg2].
2. 64-bit: args in rdi/rsi/rdx — need pop gadgets.
3. Static: no PLT, no GOT; use in-binary gadgets and syscalls.
4. No frame pointer: the frame layout shifts; measure offsets, don't assume.

## Falsifier

Falsifier — the offset math from the textbook fails because the build flags differ: always measure offsets empirically.

## Traps

- x86 (32-bit) chains put args on the stack — simpler ROP layout.
- Static binaries carry no libc — only syscalls, no system@plt.
- -fomit-frame-pointer removes saved RBP — the leave;ret pivot dies.

## Commands

```bash
readelf -h ./chal | grep -iE 'class|type'
```

## Cross-references

`saved-regs.md` · `stack-alignment.md`
