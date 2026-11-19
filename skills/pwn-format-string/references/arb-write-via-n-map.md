# Arbitrary write via %n — the count write — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a pointer you control lands as a %N$n arg | the write target | arbitrary write |
| a target address to overwrite | plant it | %n writes there |
| the count via %c/width | the value written | controlled |

## Falsifier

Falsifier — you can't plant a pointer at a %N$n position, or the write count can't reach the needed value: no controlled write.
