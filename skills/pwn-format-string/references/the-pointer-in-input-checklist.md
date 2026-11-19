# The pointer inside your input — where the arg lives — checklist

Companion to `the-pointer-in-input.md`.

## Checklist

- [ ] Your input is read as bytes — an 8-byte little-endian address at the
- [ ] Place the target address at the byte-offset inside the input where
- [ ] The arg-offset-finder locates which N reads which input bytes.
- [ ] Pack the address with struct.pack('<Q', addr).
