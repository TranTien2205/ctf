# Stack canary — leak it or write around it — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| canary in protections | need its value | leak via format-string or info-leak |
| a read leaks stack content | canary recoverable | read and reuse |
| write past the canary crashes | smashing detected | route around the word |

## Falsifier

Falsifier — no leak primitive exists and the canary blocks every write path: the class's stack route is closed; other classes (format-string, heap) may remain.
