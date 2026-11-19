# Partial overwrite — low-byte control without a full leak — case catalogue

Can't leak a full pointer? Overwrite only the low 1-2 bytes of a saved return or GOT entry — redirect to a nearby target in the same page.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | only a few bytes controllable past the bound | low-byte redirect | partial write |
| 2 | the target shares the high bytes | same page | low bytes only |
| 3 | a 2-byte overwrite reaches a nearby function | same-page redirect | the trick |

## Falsifier

Falsifier — the low-byte-controlled target doesn't include any useful gadget/function: no partial redirect is possible.
