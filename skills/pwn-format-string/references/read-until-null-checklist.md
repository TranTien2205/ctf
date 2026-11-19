# Read until null — the %s truncation — checklist

Companion to `read-until-null.md`.

## Checklist

- [ ] 1. %s prints until \x00 — a pointer's bytes containing 0x00 truncate.
- [ ] 2. For flag strings this rarely matters.
- [ ] 3. For binary data (a struct, a pointer) expect early truncation.
