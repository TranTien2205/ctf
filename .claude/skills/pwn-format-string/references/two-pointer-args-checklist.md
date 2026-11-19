# Two pointer args — read and write in one call — checklist

Companion to `two-pointer-args.md`.

## Checklist

- [ ] 1. Plant ptr A at arg N, ptr B at arg M.
- [ ] 2. %N$s derefs A (read), %M$n writes to *B.
- [ ] 3. Order matters: the count for %n includes everything printed before
