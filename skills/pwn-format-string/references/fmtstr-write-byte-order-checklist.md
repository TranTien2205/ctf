# Byte-write ordering — low-to-high vs high-to-low — checklist

Companion to `fmtstr-write-byte-order.md`.

## Checklist

- [ ] Sort targets so the needed count-values are non-decreasing.
- [ ] write value = count at that point; count = cumulative chars printed.
- [ ] A target byte smaller than the running count needs a 256-wrap pad.
- [ ] 1. List target bytes in memory order.
- [ ] 2. Reorder the %N$hhn sequence so values ascend (mod 256 wraps allowed).
- [ ] 3. Pad with %Nc between specifiers to reach each value.
