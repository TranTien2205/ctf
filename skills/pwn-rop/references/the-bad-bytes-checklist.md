# Bad bytes — the transport's constraints — checklist

Companion to `the-bad-bytes.md`.

## Checklist

- [ ] 0x00: the gets-style terminator — an address's high bytes are zeros;
- [ ] 0x0a/0x0d: the line-read terminator.
- [ ] Others the filter strips.
- [ ] Pick gadget addresses without the bad bytes.
- [ ] Compute a bad-byte value via xor instead of a literal.
- [ ] Use a non-line-based channel if the protocol offers one.
