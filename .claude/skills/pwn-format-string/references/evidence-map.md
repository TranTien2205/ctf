# Evidence — what proves each stage — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| %p reflects pointers | leak confirmed | the dump |
| AAAA.%N$p → 0x41414141 | offset confirmed | the index |
| the target addr's value changed | write confirmed | the read-back |
| execution reached your target | redirect confirmed | the behavior |

## Falsifier

Falsifier — the write's target doesn't change when %n fires: the pointer isn't at the expected arg position; re-find N.
