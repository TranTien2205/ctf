# Specifier starvation — when the fmtstr consumes the args — checklist

Companion to `starvation.md`.

## Checklist

- [ ] Each %p/%x/%s/%n consumes one argument position.
- [ ] A long run of %p before the %n walks past your planted pointer.
- [ ] Positional args %N$... don't consume — they address by index.
- [ ] 1. Keep the write early, or use positional specifiers.
- [ ] 2. Count the consuming specifiers before your target %N.
- [ ] 3. Positional %N$p/%N$n address by index — no consumption.
