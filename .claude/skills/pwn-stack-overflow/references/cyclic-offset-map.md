# Offset measurement — the cyclic pattern — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| crash with a controllable fault address | offset measurable | cyclic + fault read |
| RIP holds four pattern bytes | control proven | build the payload |
| pattern repeats but no crash at write boundary | length capped too short | not stack-smash — re-check the bound |

## Falsifier

Falsifier — the faulting register never holds pattern bytes at any length: no write reaches the saved return address. Re-check the read bound; it is probably capped below the saved-state distance.
