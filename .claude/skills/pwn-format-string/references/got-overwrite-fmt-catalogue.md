# GOT overwrite via %n — partial RELRO's prize — case catalogue

Under partial RELRO, the GOT is writable: plant a GOT slot's address as a %N$n arg and overwrite it — the next call to that import goes to your target.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | partial RELRO | GOT writable | %n to a slot |
| 2 | an import called later with controllable args | the redirect | the call |
| 3 | a GOT slot's address | the write target | plant + write |

## Falsifier

Falsifier — full RELRO: GOT read-only; no %n-to-GOT write applies.
