# Evidence — what proves each stage — checklist

Each stage has a hard signal: the leak (reflected pointers), the offset (0x41414141 at N), the write (the target's value changed), the redirect (execution went to your target).

## Checklist

- [ ] The %p leak: reflected stack words = the read primitive.
- [ ] The offset: AAAA.%N$p returning 0x41414141 = your buffer's index.
- [ ] The write: read back the target — its value changed.
- [ ] The redirect: the call/return went to your target (output or flag).

## Abort conditions

- A leak that shows only the literal 'AAAA' means the buffer isn't a printf arg.
- The write is proven by the target's changed value, not the %n syntax.

## Falsifier

Falsifier — the write's target doesn't change when %n fires: the pointer isn't at the expected arg position; re-find N.
