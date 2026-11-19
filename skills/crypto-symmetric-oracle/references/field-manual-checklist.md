# Field manual — one page per move — checklist



## Checklist

- [ ] Replay: same input twice → deterministic?
- [ ] Length: grow input → block or stream?
- [ ] Repeat: 'A'*48 → ECB fingerprint?
- [ ] Corrupt: pad-vs-MAC distinguishable?
- [ ] Tag: checked before decrypt?

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
