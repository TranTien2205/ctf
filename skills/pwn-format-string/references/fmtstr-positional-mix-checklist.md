# The positional-args requirement — all or none — checklist

Companion to `fmtstr-positional-mix.md`.

## Checklist

- [ ] 1. glibc: %N$p...%p in one call — undefined/error.
- [ ] 2. Use positional throughout for the clean case.
- [ ] 3. Or all non-positional (the arg-walk).
