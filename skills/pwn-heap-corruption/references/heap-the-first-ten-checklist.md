# The first ten minutes — the heap run — checklist

Companion to `heap-the-first-ten.md`.

## Checklist

- [ ] 1. pwn_triage the binary — protections and the dangerous imports.
- [ ] 2. afl/nm — the menu functions; strings for the glibc hint.
- [ ] 3. Run it — map the menu ops.
- [ ] 4. r2 -d — dmh the heap once to see the layout.
- [ ] 5. Free an object, read it through the program — does the data show
