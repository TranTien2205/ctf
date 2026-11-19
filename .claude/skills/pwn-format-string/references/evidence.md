# Evidence — what proves each stage

Each stage has a hard signal: the leak (reflected pointers), the offset (0x41414141 at N), the write (the target's value changed), the redirect (execution went to your target).

## Signals

| Observation | Meaning | Route |
|---|---|---|
| %p reflects pointers | leak confirmed | the dump |
| AAAA.%N$p → 0x41414141 | offset confirmed | the index |
| the target addr's value changed | write confirmed | the read-back |
| execution reached your target | redirect confirmed | the behavior |

## Steps

1. The %p leak: reflected stack words = the read primitive.
2. The offset: AAAA.%N$p returning 0x41414141 = your buffer's index.
3. The write: read back the target — its value changed.
4. The redirect: the call/return went to your target (output or flag).

## Falsifier

Falsifier — the write's target doesn't change when %n fires: the pointer isn't at the expected arg position; re-find N.

## Traps

- A leak that shows only the literal 'AAAA' means the buffer isn't a printf arg.
- The write is proven by the target's changed value, not the %n syntax.

## Cross-references

`workflow.md` · `falsifiers.md`
