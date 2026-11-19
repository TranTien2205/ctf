# Length field tricks — when the input length is the bug — checklist

The read's n is attacker-influenced or miscomputed: signed-n checks, integer wrap, off-by-one — the length IS the vulnerability.

## Checklist

- [ ] Find where the length arg comes from — user input? computed? fixed?
- [ ] If checked 'n <= sizeof(buf)' without 'n >= 0' or 'n > 0' — negative n bypasses.
- [ ] An off-by-one lets the write pass the bound by one byte — often enough for a single-byte overwrite of the saved LSB.
- [ ] A computed n that wraps (integer overflow) can be huge.

## Abort conditions

- A signed 'n <= size' check passes negative n — the classic length bug.
- Off-by-one only buys one byte — useful for canary LSB zeroing or a one-byte frame-pointer shift.
- n from a network length field can wrap through int truncation.

## Falsifier

Falsifier — the length is genuinely bounded and your input can't influence it: the read is safe; check a different input path.
