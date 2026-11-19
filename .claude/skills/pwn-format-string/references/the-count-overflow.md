# The count overflow — the count wraps


The byte-count can exceed the write width: %hhn writes count&0xff, so a
count of 0x100+ wraps — set the low byte, the high bits don't matter.

## The math

- %hhn writes count&0xff — only the low byte lands.
- Set the count so its low byte is your target byte.
- A count of 0x141 writes 0x41 via %hhn.

## Steps

1. Plan each %hhn's running count for its target byte.
2. The count mod 256 is what %hhn writes.
3. The high bits of the count are free — pad with %% or %c.

## Falsifier

The running count can't produce the needed low-byte sequence in order:
reorder the writes or use a different width.
