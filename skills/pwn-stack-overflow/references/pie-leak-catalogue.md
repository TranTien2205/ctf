# PIE leak — getting the code base under ASLR — case catalogue

PIE randomizes the binary's base: every function/gadget/data address is base+offset. A leak of ANY code/data pointer gives the base.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | PIE enabled | all addresses relative | leak a pointer |
| 2 | a read shows a code/data address | base recoverable | subtract the offset |
| 3 | a format-string or info-leak | leak primitive | use it |

## Falsifier

Falsifier — PIE on and no leak primitive exists: addresses can't be resolved; need a brute-force or a partial-overwrite trick.
