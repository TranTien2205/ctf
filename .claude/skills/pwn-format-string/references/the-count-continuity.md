# The count continuity — the running total across the call


The %n count is CUMULATIVE across the whole call: every printed byte adds
to it. Plan the sequence so each write's count is the needed value.

## The math

- Each %c/%d/%p adds its printed length to the count.
- %% adds 1 per %%.
- The %n at position k sees all bytes printed before it.

## The recipe

For byte-wise writes, sequence the specifiers so the running count's low
byte at each %hhn is the target byte.
