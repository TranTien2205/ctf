# Byte-write ordering — low-to-high vs high-to-low


Multiple %hhn writes in one call share a cumulative count — the order of
target bytes must match the order the count can produce.

## The constraint

The count only grows. To write bytes [b0,b1,b2,b3]:

- Sort targets so the needed count-values are non-decreasing.
- write value = count at that point; count = cumulative chars printed.
- A target byte smaller than the running count needs a 256-wrap pad.

## Steps

1. List target bytes in memory order.
2. Reorder the %N$hhn sequence so values ascend (mod 256 wraps allowed).
3. Pad with %Nc between specifiers to reach each value.

## Falsifier

The byte sequence can't be ordered to a non-decreasing count within the
padding budget: split across calls or reorder target slots.
