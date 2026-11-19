# Null bytes inside the fmtstr input — checklist

Companion to `fmtstr-arg-nulls.md`.

## Checklist

- [ ] 1. If input is a C string: no \x00 → can't plant most pointers directly.
- [ ] 2. Workaround: first write plants the pointer; second uses it.
- [ ] 3. Or find an existing arg that already holds a usable pointer.
