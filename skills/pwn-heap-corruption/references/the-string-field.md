# The string field — the read primitive


An object field holding a char* that show() prints: overlap the field
with your address — the show op prints arbitrary memory.

## Steps

1. Overlap a data object with a string-pointer object.
2. Write the pointer = target.
3. show() derefs it — arbitrary read.

## Falsifier

No printed-pointer field exists: the read channel needs a different
shape (crash oracle, error content).
