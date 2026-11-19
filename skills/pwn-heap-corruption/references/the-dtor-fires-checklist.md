# Destructors — the C++ free-path extras — checklist

Companion to `the-dtor-fires.md`.

## Checklist

- [ ] A vtable-corrupted object's delete fires your vfunc, THEN frees —
- [ ] Order: dtor first, free second — the call happens while the chunk is
