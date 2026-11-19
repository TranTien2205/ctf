# Many args in one call — the deep-scan fmtstr — checklist

Companion to `many-args-one-call.md`.

## Checklist

- [ ] 1. Send a long %p run — 30-60 specifiers.
- [ ] 2. Parse the reflected words in order.
- [ ] 3. Map: your input at N, canary at N+k, return addrs deeper.
