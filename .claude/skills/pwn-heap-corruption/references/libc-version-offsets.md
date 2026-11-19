# Computing libc offsets — leak to base


A leaked libc pointer becomes a base only after subtracting the right
offset — wrong offsets are the most common silent failure.

## The usual leaks

- main_arena symbol: unsorted-bin fd/bk on the first big free.
- __free_hook/__malloc_hook: derived from the arena offset.
- system/other imports: from the base once known.

## Compute

    libc_base = leaked_value - KNOWN_OFFSET

where KNOWN_OFFSET is the symbol's offset in THAT libc version —
read it from the shipped libc:

    readelf -s libc.so.6 | grep main_arena    # often absent — use:
    r2 -A libc.so.6 ; dmi libc main_arena     # or known public offsets

## Traps

- The offset differs per libc build — the 2.31 offset is not 2.35's.
- If the challenge ships its libc, compute from THAT file, not from a
  public table for a different version.

## Falsifier

The leaked value minus any plausible offset doesn't land on a page
boundary aligned to the ELF base: wrong symbol identified.
