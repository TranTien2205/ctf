# The ret sled — padding the walk


A run of `ret` gadgets: each advances rsp 8 bytes — used for
alignment insurance and to skip regions without a jump.

## The cost

Each sled entry is a qword — the budget counts them.
