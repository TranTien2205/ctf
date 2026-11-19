# Count overflow — when the byte-count wraps


The count grows monotonically but %hhn only keeps the low byte — a count
of 0x120 writes 0x20. Use the wrap to reach values below the running
count.

## Steps

1. count already 0x90, want 0x20: %144c → count 0x120 → %hhn writes 0x20.
2. The high byte (0x100) is discarded by %hhn.
3. For %hn (2 bytes): wrap at 0x10000.

## Ordering with wraps

Each wrap costs padding; a write sequence needing many wraps is long —
reorder targets to minimize wraps, or split across calls.

## Falsifier

The padding needed exceeds the input bound: the sequence can't express
the value — split the write.
