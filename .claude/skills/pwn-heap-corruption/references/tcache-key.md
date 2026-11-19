# The tcache key — 2.29+ double-free detection


glibc 2.29+ writes `e->key = tcache` into the freed chunk and checks it
on free: freeing a chunk whose key matches → "double free detected".

## Around the check

- Overwrite the key field after the free (UAF write) then free again —
  the check reads key==0 → passes.
- Or zero the key via an overflow of the freed chunk's tail.
- Or free through a different bin path (fastbin where the key isn't
  checked).
- Or corrupt `counts[]` in tcache_perthread_struct.

## Locate the key

Chunk layout after free (tcache): | prev_size | size | next | key | —
key sits 0x10 into the user area (x64).

## Falsifier

No write reaches the key field and the same-bin path is the only one:
the double-free is caught — pivot to single-free poisoning.
