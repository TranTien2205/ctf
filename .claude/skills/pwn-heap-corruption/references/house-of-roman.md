# House of roman — fastbin to __malloc_hook


A fastbin dup aimed at __malloc_hook minus an alignment offset — the
classic 2.23-era write: fake-chunk the hook region, alloc returns near
it, write the gadget over the hook. Dead on 2.35+ (no hooks).

## Steps (old glibc)

1. Fastbin dup to a fake chunk overlapping __malloc_hook - 0x23.
2. The fake chunk's size must pass the fastbin size check — the known
   0x7f alignment trick (the byte before the hook is 0x7f → size 0x70).
3. Alloc returns the fake; write the one-gadget over the hook.
4. The next malloc fires it.

## Falsifier

glibc >= 2.35: no __malloc_hook exists — the whole route is absent.
