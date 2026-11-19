# The null-arg edge — %s on a null pointer


%s on a null arg crashes (deref of 0) — a reliable primitive-detector:
if a %N$s on a zero-valued arg crashes, the deref mechanism is real.

## Signals

- %N$s on a 0 arg: crash — deref confirmed.
- %N$p on same arg: prints (nil) or 0 — the value.

## Steps

1. A null arg crashes %s — confirms the specifier mechanism is live.
2. Different from %p — %p on null just prints it.
3. The crash itself is the signal when output isn't shown.

## Falsifier

The crash doesn't happen (arg wasn't null or %s not reached): recheck
the position.
