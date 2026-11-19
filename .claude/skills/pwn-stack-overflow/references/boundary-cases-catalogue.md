# Boundary cases — where the textbook breaks — case catalogue

Each entry: the boundary, why the recipe breaks, the fix.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | 32-bit vs 64-bit | arg passing differs | x86 args on stack; x64 in regs |
| 2 | static vs dynamic | PLT/libc story differs | static = code in binary only |
| 3 | -fomit-frame-pointer | no saved RBP | leave;ret unavailable |
| 4 | tiny binary / few gadgets | chain construction hard | ret2csu or SROP or leak |

## Falsifier

Falsifier — the offset math from the textbook fails because the build flags differ: always measure offsets empirically.
