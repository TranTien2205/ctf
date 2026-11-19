# The thin binary — when gadgets are scarce


A small static-less binary may lack the pop set — the routes:

- ret2csu (the init function's gadgets).
- libc gadgets (with a leak — libc is huge).
- The PLT stubs' partial decoding.

## The falsifier

Nothing composes the needed call — reclassify or escalate.
