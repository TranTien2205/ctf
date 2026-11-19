# The write-value constraint — the count can only grow


%n writes 'bytes printed so far' — a CUMULATIVE, non-negative count. The
value you write must be reachable as a byte-count in one call.

## The constraint

- The count never decreases within one call.
- A large target value (like 0x7f...) needs byte-wise %hhn composition,
  not one %n.
- %hhn writes count&0xff — set each byte from the running count's low
  byte.

## The recipe

Build the target byte-by-byte with %hhn at increasing offsets; each
specifier's count contributes its own bytes to the running total.
