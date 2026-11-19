# Reading a menu-driven heap service — checklist

Companion to `menu-driver-map.md`.

## Checklist

- [ ] add(size) → malloc + store pointer in a global array (which index is
- [ ] delete(i) → free(ptr[i]) — and whether ptr[i] is cleared decides UAF.
- [ ] show(i) → read ptr[i] — the leak channel (dangling read gives the
- [ ] edit(i, data) → write ptr[i] — the corruption channel (dangling
