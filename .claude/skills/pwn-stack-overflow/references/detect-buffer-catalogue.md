# Detecting the buffer — finding the sink — case catalogue

White-box: grep for the read functions and array bounds. Black-box: send patterns and watch for crashes at growing lengths.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | source shows gets/strcpy/read(unbounded) | the sink is named | direct to cyclic |
| 2 | black-box crash at length N | bound = N-ish | cyclic around N |

## Falsifier

Falsifier — every read is properly bounded: no stack-corruption exists; other classes own it.
