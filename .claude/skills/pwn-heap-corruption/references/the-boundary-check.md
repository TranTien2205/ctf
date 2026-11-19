# The boundary check — which writes can reach


Before any technique: does the bug's write reach heap metadata at all?

## The test

- A data-only write (inside the object's buffer) can't corrupt
  metadata — the class needs an overflow or a freed-chunk write.
- An index-OOB reaches neighboring globals — different targets.

## Falsifier

No write path reaches outside the object's own bytes: heap-corruption
is closed; the bug is a data-write only.
