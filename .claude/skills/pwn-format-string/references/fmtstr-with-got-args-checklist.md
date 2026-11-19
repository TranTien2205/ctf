# When a GOT entry is already an arg — checklist

Companion to `fmtstr-with-got-args.md`.

## Checklist

- [ ] 1. Scan %N$p: an arg that's already a pointer is a free deref target.
- [ ] 2. %N$s on it reads the pointee — if it's a GOT entry, that's a libc
- [ ] 3. A saved-string-pointer arg reads the string.
