# The arg-size edge — %ln vs %n on x32 — map

Companion to `fmtstr-sizeof-arg.md`.

| Specifier | x86 | x64 |
|---|---|---|
| %n | 4 bytes | 4 bytes (int) |
| %ln | 4 bytes | 8 bytes |
| %lln | 8 bytes | 8 bytes |
## Falsifier
