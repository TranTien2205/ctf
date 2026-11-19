# Evidence — what proves each stage — case catalogue

Each stage has a hard signal: the leak (reflected pointers), the offset (0x41414141 at N), the write (the target's value changed), the redirect (execution went to your target).

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | %p reflects pointers | leak confirmed | the dump |
| 2 | AAAA.%N$p → 0x41414141 | offset confirmed | the index |
| 3 | the target addr's value changed | write confirmed | the read-back |
| 4 | execution reached your target | redirect confirmed | the behavior |

## Falsifier

Falsifier — the write's target doesn't change when %n fires: the pointer isn't at the expected arg position; re-find N.
