# Partial write — %hn / %hhn for byte-level control — checklist

A full %n writes a qword; %hn writes 2 bytes; %hhn writes 1. Byte-wise writes let you set a large value (like an address) without printing billions of bytes for the count.

## Checklist

- [ ] For a large address, write it byte-by-byte with %hhn at increasing offsets.
- [ ] Each %hhn writes the low byte of the count — control the count per byte.
- [ ] Write the LOW bytes first if the high bytes are already correct.
- [ ] A 2-byte redirect via %hn reaches the same page/64KB region.

## Abort conditions

- %hhn writes count&0xff — set the count so its low byte is your target byte.
- Multiple %hhn in one fmtstr write several bytes — order them.
- The count is cumulative — reset via a new call or compute the deltas.

## Falsifier

Falsifier — the byte-precision write can't compose the needed value at the reachable positions: the write is incomplete.
