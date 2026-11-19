# The free order — sequencing the corruption — checklist

Companion to `the-free-order.md`.

## Checklist

- [ ] Drain tcache (7 frees of size S) to route later frees elsewhere.
- [ ] A-B-A ordering defeats fastbin's top check.
- [ ] Free the victim LAST if you want it at the bin's head.
- [ ] Re-free after key-clearing for 2.29+ double-free.
