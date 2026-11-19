# GOT overwrite — partial RELRO — case catalogue

Under partial RELRO, the GOT stays writable: overwrite an imported function's GOT slot to point at system/another function — the next call to it goes to your target.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | partial RELRO | GOT writable | overwrite a slot |
| 2 | a function called later with a controllable arg | the call to redirect | write into its GOT |
| 3 | a write-what-where primitive | the write vector | stack smash to GOT or arb-write |

## Falsifier

Falsifier — full RELRO: the GOT is read-only; no GOT write applies.
