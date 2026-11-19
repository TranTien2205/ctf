# Partial-write ordering — which bytes first


Byte-wise address writes: write the LOW bytes first if the high bytes are
already right, or the high bytes first to shrink the count needed.

## Order

- If the target's high bytes match the existing value: only overwrite
  the low bytes.
- If the whole address differs: %hhn at each byte offset.
- A 2-byte %hn redirect reaches the same 64KB region.

## Steps

1. Compare the target to the existing value — which bytes differ?
2. Only overwrite the differing bytes.
3. Write them in an order that keeps the running count producing the
   right low bytes.

## Falsifier

The needed byte sequence can't be produced by any ordering of the
running count: the write is impossible in one call.
