# House of orange — top + FSOP composite


A no-free-needed technique: corrupt the top chunk size AND a FILE
structure so a failed alloc falls into _IO_* handling — historic;
largely dead post-2.26 (top checks + vtable check). Worth knowing the
shape, not trying first.

## Falsifier

Modern glibc rejects the top corruption and checks vtables — the
classic orange is closed; its pieces survive separately.
