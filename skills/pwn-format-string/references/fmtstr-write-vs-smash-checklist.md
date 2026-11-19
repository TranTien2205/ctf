# Fmtstr-write vs stack-smash — two writes, two classes — checklist

Companion to `fmtstr-write-vs-smash.md`.

## Checklist

- [ ] Write | Class
- [ ] a %n | format-string
- [ ] a copy past a buffer | stack-smash
- [ ] both primitives in one binary | leak + smash
