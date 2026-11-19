# Canary + PIE leak composition — defeating both at once — checklist

PIE and a canary together need TWO leaks: a code pointer for the base AND the canary word. The fmtstr's %p run can leak both in one call.

## Checklist

- [ ] Dump the %p words at all depths.
- [ ] Find the canary (ends in 00) and a code pointer (points into .text).
- [ ] base = code_ptr - known_offset; canary = the 00-word.
- [ ] Build the smash with canary preserved + base-relative addresses.

## Abort conditions

- The canary's depth and the code pointer's depth are different — read both.
- The code pointer's offset-to-base is symbol-specific — get it from the binary.

## Falsifier

Falsifier — the %p run doesn't reach the depths where both values sit: one or both stay hidden.
