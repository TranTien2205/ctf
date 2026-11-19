# Determinism — making the layout repeatable


Heap addresses differ per run (ASLR), but the LAYOUT (relative
positions) is often deterministic — exploit relative, not absolute.

## The lever

- Groom to a known RELATIVE layout; the absolute addresses come from
  the leak.
- The bin orders and chunk adjacency are stable — plan on them.

## Falsifier

The layout itself varies (threaded allocs, shared heaps): normalize
first or choose a layout-agnostic primitive.
