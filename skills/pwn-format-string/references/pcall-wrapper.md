# pcall/xpcall wrappers — the protected call


printf-family inside pcall swallows errors — a bad %s arg no longer
crashes visibly; the oracle becomes 'error swallowed' vs 'worked', still
observable via the continuation.

## Steps

1. If printf runs inside pcall: bad derefs raise internally.
2. The pcall's return value may propagate — check for a difference.
3. The %n write still works inside pcall (no error raised).

## Falsifier

pcall swallows every signal and nothing observable differs:
detection-by-crash dies; rely on write effects.
