# 32-bit fmtstr — the x86 shape — checklist

Companion to `fmtstr-32-bit.md`.

## Checklist

- [ ] 1. All args on the stack — your input appears at a low N.
- [ ] 2. %n writes 4 bytes (the whole pointer).
- [ ] 3. Addresses are 4 bytes — plant with struct.pack('<I', addr).
- [ ] 4. No register args — the first %p already reads stack data.
