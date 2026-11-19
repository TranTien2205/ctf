# Partial pointer overwrite — low-byte aims — checklist

Companion to `partial-ptr-overwrite.md`.

## Checklist

- [ ] Corrupting a saved fd's low byte: the bin points a few hundred bytes
- [ ] Overwriting a function pointer's low byte: redirects within the same
- [ ] On 2.32+, even a partially-known pos lets a low-byte mangled-fd edit
