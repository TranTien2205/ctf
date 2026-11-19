# Protection internals — what each mechanism actually does — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| canary: random word at frame end | checked before ret | trip on mismatch |
| NX: data pages non-executable | code can't run on stack | ROP instead |
| PIE: base randomized | addresses unknown | leak first |
| RELRO: GOT made read-only | no GOT write | full vs partial |

## Falsifier

Falsifier — the protection doesn't behave as named (e.g., a static binary 'has' __stack_chk_fail but doesn't use it): read the evidence, not the import list.
