# Arbitrary write via %n — the count write — case catalogue

%n writes 'the number of bytes printed so far' to a pointer argument. Control the count with %c/field-width and you write an arbitrary value to an arbitrary address — the write primitive.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | a pointer you control lands as a %N$n arg | the write target | arbitrary write |
| 2 | a target address to overwrite | plant it | %n writes there |
| 3 | the count via %c/width | the value written | controlled |

## Falsifier

Falsifier — you can't plant a pointer at a %N$n position, or the write count can't reach the needed value: no controlled write.
