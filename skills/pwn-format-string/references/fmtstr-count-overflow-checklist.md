# Count overflow — when the byte-count wraps — checklist

Companion to `fmtstr-count-overflow.md`.

## Checklist

- [ ] 1. count already 0x90, want 0x20: %144c → count 0x120 → %hhn writes 0x20.
- [ ] 2. The high byte (0x100) is discarded by %hhn.
- [ ] 3. For %hn (2 bytes): wrap at 0x10000.
