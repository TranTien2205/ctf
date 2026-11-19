# The three leaks — heap, libc, stack


- Heap leak: a chunk's own address — needed for safe-linking aims and
  fake-chunk anchoring. Sources: mangled fd inversion, a pointer the
  app prints, a UAF read of bin links.
- Libc leak: unsorted fd/bk → main_arena → base. Sources: the first
  big free's dangling read, a chunk's arena pointer.
- Stack leak: environ (libc offset) or a saved rbp/argv pointer in a
  stack-resident structure.

Each version's technique names which leaks it needs: list them before
writing a single payload byte.
