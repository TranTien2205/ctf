# Partial write — %hn / %hhn for byte-level control — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| the value is large (an address) | byte-wise write | %hhn |
| only low bytes need changing | partial overwrite | %hn/%hhn |
| a 2-byte redirect | %hn | low bytes |

## Falsifier

Falsifier — the byte-precision write can't compose the needed value at the reachable positions: the write is incomplete.
