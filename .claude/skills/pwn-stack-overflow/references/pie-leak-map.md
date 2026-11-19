# PIE leak — getting the code base under ASLR — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| PIE enabled | all addresses relative | leak a pointer |
| a read shows a code/data address | base recoverable | subtract the offset |
| a format-string or info-leak | leak primitive | use it |

## Falsifier

Falsifier — PIE on and no leak primitive exists: addresses can't be resolved; need a brute-force or a partial-overwrite trick.
