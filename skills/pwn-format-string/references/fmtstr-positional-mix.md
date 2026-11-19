# The positional-args requirement — all or none


glibc requires a format string to use positional specifiers
consistently: mixing %N$p and %p in one call errors out — pick one
style.

## Steps

1. glibc: %N$p...%p in one call — undefined/error.
2. Use positional throughout for the clean case.
3. Or all non-positional (the arg-walk).

## Falsifier

None; a consistency rule. The mixed form may still work on some libcs —
don't rely on it.
