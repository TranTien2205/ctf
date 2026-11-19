# Fmtstr in error paths — the handler case — checklist

Companion to `fmt-in-error-path.md`.

## Checklist

- [ ] 1. Identify the error path's trigger condition.
- [ ] 2. Put the specifiers in the field that lands in the printf.
- [ ] 3. The error path's frame affects the arg-offset — measure there.
