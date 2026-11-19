# Leaking the binary base — the PIE de-randomization — checklist

Companion to `fmtstr-binary-leak.md`.

## Checklist

- [ ] 1. Scan the %p dump for a 0x55..(x86-64 PIE) or module-range pointer.
- [ ] 2. Subtract its known offset (the symbol it points at — usually a return
- [ ] 3. base = leaked - offset. All binary addresses now computable.
- [ ] A saved return address points into the calling function — known
- [ ] A GOT slot pointer = base + got_offset — from readelf -r.
- [ ] A string pointer into .rodata = base + rodata_offset.
