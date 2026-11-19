# The hook endings — __free_hook/__malloc_hook


On glibc <= 2.34, __free_hook/__malloc_hook are libc data symbols
called on free/malloc — write system there, free a "/bin/sh" chunk,
the shell fires.

## The needs

- A libc leak (the hook's address).
- An arbitrary write.
- A free() call by the program (or a chain call to free).

## The boundary

glibc >= 2.35 removed the hooks — check the version.
