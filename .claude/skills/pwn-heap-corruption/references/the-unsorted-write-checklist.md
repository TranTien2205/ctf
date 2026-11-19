# Unsorted-bin writes — limited but leak-free — checklist

Companion to `the-unsorted-write.md`.

## Checklist

- [ ] corrupt tcache counts[] (write a big number → bin "full").
- [ ] set a global flag (a libio _IO_list_all marker).
- [ ] poison a size field elsewhere.
