# The fork-server canary — the constant reuse


A fork-server reuses the parent's canary across connections — brute
force it byte-by-byte: each guess that doesn't crash confirms a byte.

## The oracle

Overwrite one canary byte; if the child crashes, the byte was wrong —
8 bytes × 256 max tries.
