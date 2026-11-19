# Partial overwrite — low-byte control without a full leak — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| only a few bytes controllable past the bound | low-byte redirect | partial write |
| the target shares the high bytes | same page | low bytes only |
| a 2-byte overwrite reaches a nearby function | same-page redirect | the trick |

## Falsifier

Falsifier — the low-byte-controlled target doesn't include any useful gadget/function: no partial redirect is possible.
