# Negative numbers — the sign parse

`-3 + 5` — a regex without the `-` misses the operand; make the sign
part of the number pattern: `[-+]?\d+` (and `[-+]?` on the first
operand too).

## The sign

[-+]? on every operand — first included.
