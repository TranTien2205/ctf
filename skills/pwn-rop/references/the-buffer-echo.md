# The buffer echo — the input's placement


Know where the input lands: the buffer's address decides whether
it's a plant target (a known .bss) or stack-only (needs a pivot).

## The find

r2 -d: break after the read; the buffer's address is in the
register that held it (rdi/rsi at the read call, or rbp-offset in
the frame).
