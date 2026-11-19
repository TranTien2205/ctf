# The arg-size edge — %ln vs %n on x32 — checklist

Companion to `fmtstr-sizeof-arg.md`.

## Checklist

- [ ] Specifier | x86 | x64
- [ ] %n | 4 bytes | 4 bytes (int)
- [ ] %ln | 4 bytes | 8 bytes
- [ ] %lln | 8 bytes | 8 bytes
