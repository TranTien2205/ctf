# Pachinko / Pachinko Revisited (picoCTF 2025) — web + pwn

Flags read from live `/check` responses. Values not recorded here.

## Flag one
4 inputs (ids 5-8), 4 outputs (ids 1-4); goal is `flip` (the `GOALS.xor` the client
references is dead code). `NOT x = NAND(x,x)`, so four self-NAND gates.

## Flag two
`/check` runs `nand_checker` inside a custom 16-bit CPU emulator:

    0x0000-0x0FFF instructions   0x1000-0x1FFF output
    0x2000-0x2FFF input          0x3000-0x3FFF circuit nodes

The checker reads node offsets at 0x3000, validates each `< 0x1000`, then
**multiplies by 2** to index the inputs array. Write 0xfff to an output node and
invert it to get 0xf000; scaled that is 0xe000, and `0xe000 + 0x2000 & 0xffff == 0`
wraps into instruction memory. That 2-byte arbitrary write appends flag.bin's body
(load_imm r0..r3 = 0x6f73/0x6563/0x2e69/0x6f00, flag_magic 0x0e, halt 0x0f) after the
processing loop, so the CPU executes flag_magic before halting.

## What cost time
Black-box probing stalled for a long while: unassigned nodes all read 0, and ~50% of
ids "passed" a single oracle trial purely by chance. One id survived six trials and
was a false positive (8/12 on recheck) — exactly the count chance predicts. The
signal was never there; the class was wrong.
