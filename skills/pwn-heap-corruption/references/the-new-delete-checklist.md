# new/delete — the C++ operators — checklist

Companion to `the-new-delete.md`.

## Checklist

- [ ] new runs the ctor AFTER alloc — a ctor writing fields is post-alloc.
- [ ] delete runs the dtor BEFORE free — a call window.
- [ ] Sized delete (2.34+) may check the size argument.
