# Number formats — %d %u %o for read/count


Besides %p/%x, integer specifiers (%d, %u, %o) also leak arg values as
decimal/octal — and they pump the count for %n writes.

## Use

- %d/%u/%o read args like %x but format differently — same leak.
- As count-pumps they're interchangeable with %c.
- If hex chars are filtered from output, %d still leaks as decimal.

## Falsifier

None; alternative read forms only.
