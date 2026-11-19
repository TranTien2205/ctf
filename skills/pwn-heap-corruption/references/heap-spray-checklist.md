# Heap spray — flooding the space — checklist

Companion to `heap-spray.md`.

## Checklist

- [ ] 1. Allocate many objects filled with your pattern (gadget bytes, a
- [ ] 2. Free in a pattern that scatters them across bins.
- [ ] 3. A UAF/dangling read hits sprayed content instead of metadata.
- [ ] Blind heap corruption: you can't aim but can saturate.
- [ ] ASLR'd heap: spray enough that ANY heap pointer likely lands in your
- [ ] Memory caps bound the spray.
- [ ] The spray doesn't give control — only probability.
