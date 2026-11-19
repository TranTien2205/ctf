# Composing heap with other classes


Heap bugs compose:

- heap-leak → stack overflow: the leak's stack addr feeds the smash.
- fmtstr on a heap buffer: the %n write IS the heap corruption.
- heap → ROP: the write lands a ROP chain on a known stack/heap addr.
- heap → FSOP: a write inside libc's data.

The primitive chain often spans classes — the boundary between them is
where one primitive feeds the next.
