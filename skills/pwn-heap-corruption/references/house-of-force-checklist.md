# House of force — top-chunk size corruption — checklist

Companion to `house-of-force.md`.

## Checklist

- [ ] 1. Reach the top chunk's size word via an overflow from the chunk below.
- [ ] 2. Write size = 0xffffffffffffffff (or huge).
- [ ] 3. malloc(X) where X moves the top to target - top_size.
- [ ] 4. The next malloc's user area IS your target — write into it.
- [ ] glibc 2.29+: `malloc_printerr` catches the corrupted top size in most
- [ ] Still works where the size check is bypassable or old glibc.
