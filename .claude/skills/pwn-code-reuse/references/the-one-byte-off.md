# The one-byte-off — LSB redirects


A write that only reaches a pointer's low byte can still redirect
within the page — the LSB redirect needs no full leak.

## Use

- A saved return address's low byte: redirect within the same
  function's region.
- A function pointer's low byte: within the same 64KB.

## Falsifier

The needed redirect crosses a page boundary: a fuller write is
required.
