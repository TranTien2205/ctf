# Heap falsifiers — the observations that close routes — map

Companion to `falsifiers.md`.

| Observation | Route closed |
|---|---|
| free() nulls the pointer, bounds-checked indexes | the class itself |
| tcache key check fires on every double-free | naive tcache dup |
| safe-linking with no heap leak | fd-poisoning |
| glibc >= 2.35 | __free_hook/__malloc_hook routes |
| full fake-chunk checks on free | house-of-spirit unless both fields forge |
| only exact-size allocs | splitting/remainder techniques |
| no alloc/free ordering control | grooming-dependent techniques |
| all writes stay in user data | metadata corruption |
| N-bit+arena can't be faked | house-of-mind |
| mmap'd target object | everything heap-resident |
