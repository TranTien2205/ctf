# Nested argument layout — the callee's frame view — checklist

Companion to `nested-arg-layout.md`.

## Checklist

- [ ] %1-%6 (x64): the caller's register args to printf.
- [ ] %7+: the caller's stack-resident args + memory above.
- [ ] Your input buffer sits wherever the caller placed it.
