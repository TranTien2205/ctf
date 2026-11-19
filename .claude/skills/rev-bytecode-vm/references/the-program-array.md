# The program array — the VM's byte stream

The custom VM's program is a byte array — embedded in the binary
(.rodata), a file, or an argument. Decode it against the opcode
table.

## Locate it

- `iz`/`strings` for a static buffer; the .rodata section.
- A file the VM reads.
- Passed as an argument.

## Decode

Walk pc: each byte is an opcode or an immediate. Per the table:

    pc=0: 0x10 read_char     (ip->1)
    pc=1: 0x01 0x37          push 0x37
    pc=3: 0x02               xor
    ...

## The pattern

Flag-checkers are a linear read-transform-cmp chain — the decoded
program reads as `read[i]; op; cmp expected[i]` repeating.

## The counting trick

Count read ops = flag length; count cmps = number of checked bytes.
