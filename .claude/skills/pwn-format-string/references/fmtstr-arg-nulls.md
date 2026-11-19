# Null bytes inside the fmtstr input


The format input often can't contain \x00 (it's a C string) — but planted
pointers and high-byte counts may need \x00 bytes in the input.

## Steps

1. If input is a C string: no \x00 → can't plant most pointers directly.
2. Workaround: first write plants the pointer; second uses it.
3. Or find an existing arg that already holds a usable pointer.

## Falsifier

The needed pointer contains \x00 bytes and no writable staging slot
exists: pointer-planting via input is impossible.
