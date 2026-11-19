# Fmtstr + separate info-leak — two primitives, one chain — checklist

Companion to `fmtstr-plus-infoleak.md`.

## Checklist

- [ ] 1. Use whatever leak exists — it doesn't have to be the fmtstr itself.
- [ ] 2. An uninit stack read, a debug dump, an error message — all are leaks.
- [ ] 3. Feed the values into the %n write's target/value.
