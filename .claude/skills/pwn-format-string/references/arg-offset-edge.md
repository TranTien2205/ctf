# Arg-offset edge cases — when AAAA.%N$p misleads


0x41414141 can appear coincidentally in stack memory — and your input may
appear at MULTIPLE N. Verify with a longer marker.

## Steps

1. Use a longer marker: 'AAAABBBB' → look for the 8-byte value.
2. Your input may appear at multiple positions — test each for
   writability.
3. 'AAAA' could align across two args — check adjacent N.

## Falsifier

The found N doesn't actually address your input: re-scan with a longer
marker.
