# End to end — the SIMD compare


A pcmpeqb compare of 16-byte blocks:

1. The two operand addresses: input's buffer and expected's.
2. Dump the expected block.
3. The block's bytes = the answer (or per-block, if multi-block).
