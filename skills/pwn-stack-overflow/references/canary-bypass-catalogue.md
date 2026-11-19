# Stack canary — leak it or write around it — case catalogue

A stack canary is a random word placed before the saved frame; smashing past it trips __stack_chk_fail. The bypass is always the same shape: get the canary's value, keep it intact in your payload.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | canary in protections | need its value | leak via format-string or info-leak |
| 2 | a read leaks stack content | canary recoverable | read and reuse |
| 3 | write past the canary crashes | smashing detected | route around the word |

## Falsifier

Falsifier — no leak primitive exists and the canary blocks every write path: the class's stack route is closed; other classes (format-string, heap) may remain.
