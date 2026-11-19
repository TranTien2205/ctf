# Uninitialized read as a leak primitive

A buffer returned/read without full initialization carries stale stack bytes — pointers, the canary, addresses — a leak without a format string.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| read returns more than was written | stale bytes leak | a pointer/canary |
| a struct with padding returned raw | padding bytes leak | a pointer |
| a partially-filled buffer dumped | the tail holds stale data | the leak |

## Steps

1. Find a read that returns more bytes than the write set (uninit tail).
2. The stale bytes are previous stack content — a canary, a return address, a heap pointer.
3. Read the needed value from the right byte offset in the dump.
4. Use the leaked value in the overflow chain.

## Falsifier

Falsifier — the buffer is fully written before being read: no stale bytes; no leak.

## Traps

- The stale bytes vary per call — but the CANARY and return addresses are stable within a process.
- An uninit read is data-dependent — the offset to the canary varies; measure once.

## Cross-references

`canary-bypass.md` · `pie-leak.md`
