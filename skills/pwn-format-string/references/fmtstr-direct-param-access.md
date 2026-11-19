# Direct parameter access — %N$x semantics


%N$ reads the Nth argument directly — no walking. It's the only reliable
way to reach deep args and to reuse the same arg twice.

## Semantics

- %7$p — the 7th arg slot, as a pointer.
- %7$s — deref the 7th arg as a string.
- %7$n — write count to the 7th arg as a pointer.
- %7$hhn — same, byte-width.
- The arg index N counts varargs: on x64, 1-6 are regs, 7+ are stack.

## Boundaries

- N has a platform max (often large, but the input length caps it).
- Reusing N twice in one call is legal — both read arg 7.

## Falsifier

N beyond what printf supports: lower N or use sequential specifiers.
