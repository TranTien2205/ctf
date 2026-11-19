# Rehearsing the count — dry-running the arithmetic


Before sending the write, dry-run the count arithmetic on paper: which
bytes print before each %hhn, and whether the low byte lands right.

## Steps

1. List the target bytes low→high.
2. Assign a printed-count to each %hhn so count&0xff = the byte.
3. Order specifiers so the running count hits each needed low byte.
4. Between writes, pad with %c/%% to reach the next byte's count.

## Falsifier

The byte sequence is unreachable (a needed byte's count can't be produced
without reducing the total): reorder or split across calls.
