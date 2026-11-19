# The dangling arg — reading a stale pointer


An arg may hold a stale/freed pointer — %s on it either reads garbage or
crashes. Usually harmless noise; occasionally a freed-object pointer.

## Steps

1. Some args are stale pointers — %s on them reads whatever's there now.
2. A crash — the pointer is dead.
3. Garbage output — the memory is valid but stale: possibly useful data.

## Falsifier

None; noise to filter from the real leak.
