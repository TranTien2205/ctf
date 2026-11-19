# The corruption window — how far the bug reaches — checklist

Companion to `the-window.md`.

## Checklist

- [ ] A 1-byte overflow → size LSB only (off-by-null family).
- [ ] An 8-byte write past the end → full size field.
- [ ] A bounded OOB index → a fixed slice of a struct.
