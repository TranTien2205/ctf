# Length field tricks — when the input length is the bug

The read's n is attacker-influenced or miscomputed: signed-n checks, integer wrap, off-by-one — the length IS the vulnerability.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| read(fd,buf,n) where n is from input | n controllable | set n huge |
| n checked as signed int, only 'n <= size' | negative n passes | n = -1 or large-positive |
| off-by-one in the bound | one extra byte | a 1-byte overwrite |

## Steps

1. Find where the length arg comes from — user input? computed? fixed?
2. If checked 'n <= sizeof(buf)' without 'n >= 0' or 'n > 0' — negative n bypasses.
3. An off-by-one lets the write pass the bound by one byte — often enough for a single-byte overwrite of the saved LSB.
4. A computed n that wraps (integer overflow) can be huge.

## Falsifier

Falsifier — the length is genuinely bounded and your input can't influence it: the read is safe; check a different input path.

## Traps

- A signed 'n <= size' check passes negative n — the classic length bug.
- Off-by-one only buys one byte — useful for canary LSB zeroing or a one-byte frame-pointer shift.
- n from a network length field can wrap through int truncation.

## Commands

```bash
r2 -A ./chal && pdf @ <vuln> | grep -iE 'read|call|cmp'
```

## Cross-references

`read-family.md`
