# Arbitrary read via %s — dereference a planted pointer — case catalogue

%s dereferences a pointer argument — plant a pointer where a %N$s arg reads it and %s prints the memory it points to. An arbitrary read in one specifier.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a pointer you control lands as a %N$s arg | %s derefs it | arbitrary read |
| 2 | a target address to read | plant it as the arg | %s prints *ptr |
| 3 | need to read flag/.rodata/secret | the read primitive | %s at the ptr |

## Falsifier

Falsifier — you can't plant a pointer where a %N$s arg reads it: no controlled dereference; only the leak-via-%p path remains.
