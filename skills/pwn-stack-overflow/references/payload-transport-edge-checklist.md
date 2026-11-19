# Payload transport edge cases — encoding and framing — checklist

Companion to `payload-transport-edge.md`.

## Checklist

- [ ] The payload travels through a protocol with its own encoding: base64, a
- [ ] length field, a fixed frame — the binary bytes must survive it.
- [ ] A base64-encoded field — encode the payload first.
- [ ] A length-prefixed frame — the length field bounds the payload.
- [ ] A text-protocol field — only printable bytes survive.
- [ ] A binary socket — raw bytes pass.
- [ ] Match the payload's encoding to the transport's; a banned byte or a
- [ ] framing truncation kills the payload silently.
