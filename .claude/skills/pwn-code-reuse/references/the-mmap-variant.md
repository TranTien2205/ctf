# mmap variants — the flags question


mmap's flags arg (r10, syscall arg4) is the scarce register — variants:

- MAP_ANONYMOUS|MAP_PRIVATE = 0x22 — the usual.
- If r10 can't be set: use MAP_SHARED with a valid fd, or a different
  alloc path (brk syscall = 12).
