# The environ leak — stack from libc — checklist

Companion to `environ-leak.md`.

## Checklist

- [ ] 1. libc base known (unsorted leak).
- [ ] 2. environ_offset in that libc → environ_addr = base + offset.
- [ ] 3. Arbitrary-read environ: the value is a stack pointer near the top
- [ ] 4. Stack addresses now derivable — ret-addr slots computable.
