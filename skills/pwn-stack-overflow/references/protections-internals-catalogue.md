# Protection internals — what each mechanism actually does — case catalogue

Each protection is a specific mechanism with a specific failure mode — knowing the internals tells you the bypass.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | canary: random word at frame end | checked before ret | trip on mismatch |
| 2 | NX: data pages non-executable | code can't run on stack | ROP instead |
| 3 | PIE: base randomized | addresses unknown | leak first |
| 4 | RELRO: GOT made read-only | no GOT write | full vs partial |

## Falsifier

Falsifier — the protection doesn't behave as named (e.g., a static binary 'has' __stack_chk_fail but doesn't use it): read the evidence, not the import list.
