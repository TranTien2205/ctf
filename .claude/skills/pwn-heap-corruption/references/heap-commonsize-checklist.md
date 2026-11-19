# The common size classes in CTF services — checklist

Companion to `heap-commonsize.md`.

## Checklist

- [ ] 0x30-0x40: small objects (id + one ptr + small buf).
- [ ] 0x90-0x100: medium (name + desc).
- [ ] 0x200+: large (big content fields).
