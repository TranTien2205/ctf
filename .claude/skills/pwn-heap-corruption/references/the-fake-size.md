# Forging the size field — valid values


A fake chunk's size must satisfy: >= 0x20, 0x10-aligned, with the next
chunk's size field also sane — the two-field forge.

## The pair

    fake @ P:      size = 0x41      (S | P)
    fake_next @ P+0x40: size = 0x21 (any sane value)

free(P+0x10) checks both — forge both.

## Falsifier

Only one field is writable: the check on the other kills it — pick a
technique needing fewer forged fields.
