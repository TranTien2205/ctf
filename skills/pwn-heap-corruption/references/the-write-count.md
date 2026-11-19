# How many writes — the primitive's cost


Count what the technique needs:

- tcache poison (post-2.32): 1 leak-read + 1 fd write + 2 allocs + 1
  payload write.
- unsorted leak: 1 free + 1 dangling read.
- fastbin dup: 3 frees + 3 allocs.
- off-by-one overlap: 1 byte + 1 free + 1 realloc.

The program's op budget may cap the sequence — count the ops first.

## Falsifier

The needed sequence exceeds the program's op surface (e.g. only one
free ever callable): the technique can't run.
