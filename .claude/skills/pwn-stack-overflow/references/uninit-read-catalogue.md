# Uninitialized read as a leak primitive — case catalogue

A buffer returned/read without full initialization carries stale stack bytes — pointers, the canary, addresses — a leak without a format string.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | read returns more than was written | stale bytes leak | a pointer/canary |
| 2 | a struct with padding returned raw | padding bytes leak | a pointer |
| 3 | a partially-filled buffer dumped | the tail holds stale data | the leak |

## Falsifier

Falsifier — the buffer is fully written before being read: no stale bytes; no leak.
