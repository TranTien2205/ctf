# UAF to overlap — the two-step


A UAF isn't itself the goal — the goal is two live objects sharing
memory. The overlap is where corruption becomes control.

## The recipe

1. Free object A (size S). Pointer p still names it.
2. Alloc object B size S → B reuses A's slot (tcache LIFO).
3. p (stale) and B (live) alias the same bytes.
4. Write via p → corrupts B's fields; read via p → leaks B's fields.

## Choosing B

- B with a function pointer/vtable → forge the call target.
- B with a data pointer (name/desc field) → forge the read/write target.
- B with an index or size field → expand the primitive.

## Falsifier

No allocation of size S ever reuses A's slot (different size classes or
a different bin): the alias never forms.
