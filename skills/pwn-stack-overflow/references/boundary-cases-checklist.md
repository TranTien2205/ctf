# Boundary cases — where the textbook breaks — checklist

Each entry: the boundary, why the recipe breaks, the fix.

## Checklist

- [ ] 32-bit: args on the stack — chain is [func][ret][arg1][arg2].
- [ ] 64-bit: args in rdi/rsi/rdx — need pop gadgets.
- [ ] Static: no PLT, no GOT; use in-binary gadgets and syscalls.
- [ ] No frame pointer: the frame layout shifts; measure offsets, don't assume.

## Abort conditions

- x86 (32-bit) chains put args on the stack — simpler ROP layout.
- Static binaries carry no libc — only syscalls, no system@plt.
- -fomit-frame-pointer removes saved RBP — the leave;ret pivot dies.

## Falsifier

Falsifier — the offset math from the textbook fails because the build flags differ: always measure offsets empirically.
