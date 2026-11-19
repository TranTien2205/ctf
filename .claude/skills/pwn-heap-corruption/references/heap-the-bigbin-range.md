# Largebin ranges — the size bands


Large bins group by size bands (each bin covers a range) — insert walks
within the band by size: the banding decides the walk order.

## The bands (x64, roughly)

    64-byte bands under 0x400; then 512-byte bands; then coarser.

## Falsifier

The victim's band and your insertion's band differ: the walk never
reaches it.
