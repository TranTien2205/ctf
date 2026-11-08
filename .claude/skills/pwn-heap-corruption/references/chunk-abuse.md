# Heap chunk abuse

Heap bugs are almost never "corrupt RIP directly". The primitive is a
*shape*: get the allocator to hand back two chunks that overlap, then write
through one to control the other's metadata or contents. Work the shape,
not the crash.

## The allocator decides the technique — check glibc version first

```bash
ldd --version | head -1          # glibc version = which tcache rules apply
```

| glibc | What changed |
|---|---|
| < 2.26 | no tcache — fastbins/double-free harder to protect |
| 2.26-2.31 | tcache on, no count check on double-free |
| ≥ 2.32 | tcache double-free detection + `fd` safe-linking (heap pointer XOR) |
| ≥ 2.34 | hooks removed — `__malloc_hook`/`__free_hook` are gone |

`tools/pwn_triage.py` reports the linked libc; the version row decides which
abuse is even *possible*.

## The three shapes that win most CTFs

**tcache poisoning** (≥ 2.26): free a chunk twice (double-free) or corrupt
`fd` on a freed tcache/fastbin chunk → next two `malloc`s return your chosen
address. With safe-linking (≥2.32) the `fd` write needs `target ^ (chunk>>12)`
— you need a heap leak to compute the mask.

**unsorted/small-bin leak**: free a large-ish chunk (> tcache max, or fill
tcache first) → its `fd`/`bk` point into `main_arena` → a use-after-free read
leaks a libc address. The libc leak is almost always the first real goal —
ASLR is dead once you have it.

**overlapping via size corruption**: write past a chunk's end to enlarge the
next chunk's `size` field → free+malloc returns the same memory as two
objects → overlapping pointers → write where you can't reach.

## The win targets after overlap

| You control | Write to |
|---|---|
| a freed chunk's `fd`/`bk` | arbitrary allocation → GOT (partial RELRO), `__free_hook` (<2.34), return addr |
| a function pointer in a structure | next call is yours |
| `top chunk` size | house-of-force-style (old glibc) |
| `tcache_perthread`/`mp_` | allocator-wide control |

## Working the shape

```text
1. allocate  A B C    (guard chunks between targets stop consolidation)
2. free B            -> lands in tcache or bin
3. trigger UAF/overflow on B's header
4. malloc twice      -> second pointer overlaps or points where you wrote
5. read leak -> compute libc -> write target -> trigger
```

Always pad with guard allocations: an overflowing write that touches a free
chunk's metadata crashes on the wrong thing.

## Falsifier

No heap-allocated buffer is attacker-sized + attacker-freed + attacker-read —
every object is fixed-size stack/global, or the allocator is a custom slab
with no metadata in-band. Without a free+reuse cycle there is no shape to abuse.

## Traps

- tcache fills to 7 per size — free >7 same-size chunks to push past it into
  the fastbin/unsorted path where the leak lives.
- `fd` safe-linking means the raw write value is `target ^ (ptr>>12)` — an
  unmasked address never lands.
- A double-free that glibc detects aborts before the second alloc; same-size
  alternate frees (`A B A`) walk around the check.
- The crash on `malloc` is *detection*, not the bug — the corruption happened
  one write earlier.
