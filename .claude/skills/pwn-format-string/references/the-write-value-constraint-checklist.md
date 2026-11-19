# The write-value constraint — the count can only grow — checklist

Companion to `the-write-value-constraint.md`.

## Checklist

- [ ] The count never decreases within one call.
- [ ] A large target value (like 0x7f...) needs byte-wise %hhn composition,
- [ ] %hhn writes count&0xff — set each byte from the running count's low
