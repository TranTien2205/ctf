# Verifying the leak — the sanity checks — checklist

Companion to `the-leak-verify.md`.

## Checklist

- [ ] Range: 0x55..../0x56.... (PIE binary) or 0x7f.... (libc/stack).
- [ ] Alignment: a mapped address's low 12 bits vary; a base is
- [ ] Distance: two leaks from the same region should be a known delta
