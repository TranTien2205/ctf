# The first %p — confirming the primitive exists


Before ANY other work: send one %p. If the output shows a pointer-shaped
value, the format string is live — the cheapest confirmation in binary
exploitation.

## Steps

1. Send a single %p through the input channel.
2. Output shows 0x... → primitive confirmed.
3. Output shows literal '%p' or nothing → the input isn't the format.

## Falsifier

The %p echoes back literally: the input was an argument to a literal
format — class closed, no further work.
