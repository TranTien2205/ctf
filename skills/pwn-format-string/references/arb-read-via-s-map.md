# Arbitrary read via %s — dereference a planted pointer — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| a pointer you control lands as a %N$s arg | %s derefs it | arbitrary read |
| a target address to read | plant it as the arg | %s prints *ptr |
| need to read flag/.rodata/secret | the read primitive | %s at the ptr |

## Falsifier

Falsifier — you can't plant a pointer where a %N$s arg reads it: no controlled dereference; only the leak-via-%p path remains.
