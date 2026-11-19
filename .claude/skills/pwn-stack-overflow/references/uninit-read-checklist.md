# Uninitialized read as a leak primitive — checklist

A buffer returned/read without full initialization carries stale stack bytes — pointers, the canary, addresses — a leak without a format string.

## Checklist

- [ ] Find a read that returns more bytes than the write set (uninit tail).
- [ ] The stale bytes are previous stack content — a canary, a return address, a heap pointer.
- [ ] Read the needed value from the right byte offset in the dump.
- [ ] Use the leaked value in the overflow chain.

## Abort conditions

- The stale bytes vary per call — but the CANARY and return addresses are stable within a process.
- An uninit read is data-dependent — the offset to the canary varies; measure once.

## Falsifier

Falsifier — the buffer is fully written before being read: no stale bytes; no leak.
