# GOT overwrite — partial RELRO — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| partial RELRO | GOT writable | overwrite a slot |
| a function called later with a controllable arg | the call to redirect | write into its GOT |
| a write-what-where primitive | the write vector | stack smash to GOT or arb-write |

## Falsifier

Falsifier — full RELRO: the GOT is read-only; no GOT write applies.
