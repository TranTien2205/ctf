# First-fit and bin order — where allocs come from


malloc() serves requests in a fixed order: tcache → fastbin → unsorted
(one pass) → small/large → top → mmap. Knowing the order predicts which
freed chunk the next alloc returns.

## Order

1. tcache: exact-size match, LIFO.
2. fastbin: exact-size match, LIFO.
3. unsorted: first-fit, one scan — leftovers get sorted into
   small/large bins.
4. small/large: best-fit sorted lists.
5. top chunk: split from the wilderness.
6. mmap: huge requests skip the heap entirely.

## Exploitation reading

- Same-size LIFO: the last freed is the next returned — the basis of
  every dup.
- Large allocs skip tcache — they hit unsorted/bin paths directly.

## Falsifier

Your predicted return order differs from observed — re-check the size
class and which bins that size touches.
