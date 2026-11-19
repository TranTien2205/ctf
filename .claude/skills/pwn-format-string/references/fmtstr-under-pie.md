# Fmtstr under PIE — every address needs the base


Under PIE, GOT/data/function addresses are all base+offset — the %n
write's target AND value need the leaked base.

## Steps

1. Leak a code pointer from the %p dump.
2. base = code_ptr - its_offset.
3. All target addresses = base + offset; write values likewise.

## Falsifier

No code pointer leaks at any readable N: PIE can't be defeated via this
call; need another primitive.
