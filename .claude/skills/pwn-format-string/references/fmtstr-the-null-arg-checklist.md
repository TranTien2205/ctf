# The null-arg edge — %s on a null pointer — checklist

Companion to `fmtstr-the-null-arg.md`.

## Checklist

- [ ] %N$s on a 0 arg: crash — deref confirmed.
- [ ] %N$p on same arg: prints (nil) or 0 — the value.
- [ ] 1. A null arg crashes %s — confirms the specifier mechanism is live.
- [ ] 2. Different from %p — %p on null just prints it.
- [ ] 3. The crash itself is the signal when output isn't shown.
