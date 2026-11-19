# Boundary cases — where the textbook breaks — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| 32-bit vs 64-bit | arg passing differs | x86 args on stack; x64 in regs |
| static vs dynamic | PLT/libc story differs | static = code in binary only |
| -fomit-frame-pointer | no saved RBP | leave;ret unavailable |
| tiny binary / few gadgets | chain construction hard | ret2csu or SROP or leak |

## Falsifier

Falsifier — the offset math from the textbook fails because the build flags differ: always measure offsets empirically.
