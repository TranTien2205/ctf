# Canary + PIE leak composition — defeating both at once

PIE and a canary together need TWO leaks: a code pointer for the base AND the canary word. The fmtstr's %p run can leak both in one call.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| canary + PIE | two leaks needed | the %p run |
| a %p at the right depths | both values | read them |
| a code pointer + a 00-ending word | base + canary | the leak |

## Steps

1. Dump the %p words at all depths.
2. Find the canary (ends in 00) and a code pointer (points into .text).
3. base = code_ptr - known_offset; canary = the 00-word.
4. Build the smash with canary preserved + base-relative addresses.

## Falsifier

Falsifier — the %p run doesn't reach the depths where both values sit: one or both stay hidden.

## Traps

- The canary's depth and the code pointer's depth are different — read both.
- The code pointer's offset-to-base is symbol-specific — get it from the binary.

## Cross-references

`leak-via-p.md` · `skip-canary-by-write.md`
