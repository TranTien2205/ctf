# Heap evidence — what counts as a signal — checklist

Companion to `evidence.md`.

## Checklist

- [ ] leak: a printed value that is a heap/libc/stack address — verified
- [ ] overlap: marker written via object A read back via object B.
- [ ] write: the target slot's changed bytes (read-back or behavior).
- [ ] redirect: a call/return/free that fires your pointer.
