# Length field tricks — when the input length is the bug — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| read(fd,buf,n) where n is from input | n controllable | set n huge |
| n checked as signed int, only 'n <= size' | negative n passes | n = -1 or large-positive |
| off-by-one in the bound | one extra byte | a 1-byte overwrite |

## Falsifier

Falsifier — the length is genuinely bounded and your input can't influence it: the read is safe; check a different input path.
