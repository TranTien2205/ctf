# Writing zero — the count-can't-shrink edge — checklist

Companion to `write-zero-bytes.md`.

## Checklist

- [ ] 1. To write a low byte of 0x00 via %hhn: get the count to a multiple of
- [ ] 256.
- [ ] 2. If the count already passed it — wrap: add 256-k padding.
- [ ] 3. For a full %n write of 0: impossible mid-call; do it as the FIRST
