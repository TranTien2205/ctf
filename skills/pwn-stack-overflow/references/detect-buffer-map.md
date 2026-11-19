# Detecting the buffer — finding the sink — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| source shows gets/strcpy/read(unbounded) | the sink is named | direct to cyclic |
| black-box crash at length N | bound = N-ish | cyclic around N |

## Falsifier

Falsifier — every read is properly bounded: no stack-corruption exists; other classes own it.
