# GOT overwrite via %n — partial RELRO's prize — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| partial RELRO | GOT writable | %n to a slot |
| an import called later with controllable args | the redirect | the call |
| a GOT slot's address | the write target | plant + write |

## Falsifier

Falsifier — full RELRO: GOT read-only; no %n-to-GOT write applies.
