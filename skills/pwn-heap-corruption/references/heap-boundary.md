# The class boundary — heap vs stack vs index


- Heap corruption: the allocator's state is the target — bins, sizes,
  links.
- Stack overflow: linear buffer → return address — different class
  (pwn-stack-overflow).
- OOB index on an object array: the array's neighbors, not the heap —
  a different primitive.
- A fmtstr on heap data: the %n write is fmtstr, not heap-corruption —
  the class names the BUG, not the technique it enables.

The boundary test: does the corruption go THROUGH allocator state? If
yes → this class. If it crosses a boundary into linear memory → stack.
