# The frame pointer — rbp's role


saved rbp sits between the buffer and saved rip — its value matters
only for leave;ret pivots: rbp = the pivot target.

## The two cases

- Normal chain: the saved rbp slot is padding — its value doesn't
  matter.
- Pivot chain: the saved rbp = the target region's address.
