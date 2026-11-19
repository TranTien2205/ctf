# The length check — the first gate

Many checkers verify the flag length FIRST — read the length cmp
before the byte checks; it names the flag length.

## The decode

    0x50          ; len
    0x01 0x1d     ; push 29
    0x20          ; cmp
    0x30 +N       ; jz continue

Flag length = 29. Use it to bound the brute or the inversion.
