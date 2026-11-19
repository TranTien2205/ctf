# Reading the delete op — clear or dangling — checklist

Companion to `the-menu-free.md`.

## Checklist

- [ ] delete(i): free(ptr[i]); ptr[i]=NULL → clean, no UAF from this path.
- [ ] delete(i): free(ptr[i]); → ptr[i] dangles → UAF open.
- [ ] delete(i) missing bounds → OOB free of an arbitrary pointer.
