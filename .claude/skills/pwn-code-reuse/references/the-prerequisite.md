# The prerequisite — IP control first


Code reuse presupposes control of the instruction pointer: a confirmed
stack or format-string overwrite that already lands execution where you
point it. This skill begins after that confirmation.

## The confirmation

- A cyclic offset discovered and verified — the register holds your
  bytes at the overwrite point.
- Or a %n write landing on a call slot.
- If IP control isn't proven, this isn't the class yet — return to the
  corruption primitive.

## Falsifier

No control of the instruction pointer: code-reuse content is premature
— fix the upstream primitive first.
