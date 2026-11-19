# Payload inside the input limits — fitting the chain — checklist

Companion to `payload-in-limits.md`.

## Checklist

- [ ] The read's n or the protocol's framing bounds your input — the whole
- [ ] chain must fit inside it. A 100-byte read can't hold a 5-gadget chain.
- [ ] A 60-byte read on x64 fits ~7 qwords: pad + a few gadgets.
- [ ] A length-prefixed protocol caps the frame.
- [ ] A two-stage where stage-2 lands in a larger buffer.
- [ ] Count the chain's qwords against the read bound; if it doesn't fit,
- [ ] pivot to a bigger region or split across stages.
