# Remote vs local — the libc must match — checklist

Companion to `remote-vs-local.md`.

## Checklist

- [ ] The challenge ships a libc → use THAT file for every offset.
- [ ] No shipped libc → leak and identify (a few known symbol distances
- [ ] Docker base image stated → pull its libc version.
