# Length field tricks — when the input length is the bug — case catalogue

The read's n is attacker-influenced or miscomputed: signed-n checks, integer wrap, off-by-one — the length IS the vulnerability.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | read(fd,buf,n) where n is from input | n controllable | set n huge |
| 2 | n checked as signed int, only 'n <= size' | negative n passes | n = -1 or large-positive |
| 3 | off-by-one in the bound | one extra byte | a 1-byte overwrite |

## Falsifier

Falsifier — the length is genuinely bounded and your input can't influence it: the read is safe; check a different input path.
