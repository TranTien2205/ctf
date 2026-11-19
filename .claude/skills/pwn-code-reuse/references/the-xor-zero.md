# Zeroing registers — xor/mov substitutes


When a pop gadget is missing, zeroing gadgets substitute:
`xor eax, eax; ret`, `mov edx, 0; ret`, `xor rdx, rdx; ret`.

## The search

    r2 -A ./chal ; /R xor rdx
    r2 -A ./chal ; /R mov rdx, 0

## The note

- xor reg,reg clears the whole register — good for NULL args.
- On x86-64, writing the 32-bit register zeroes the top — xor edx,edx
  clears rdx fully.

## Falsifier

No zeroing gadget and no pop: the register can't be controlled — a
different call convention is needed.
