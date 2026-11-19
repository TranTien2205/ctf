# A worked example — the menu service end to end


Service: add/del/show/edit over a 16-slot array; glibc 2.31; partial
RELRO; PIE off.

## The run

1. add(0x80) x8 — fill slots.
2. del(0)..del(6) — fill tcache[0x90]; del(7) → unsorted.
3. show(7) — the dangling read leaks main_arena → libc base.
4. edit(0) — tcache fd = &__free_hook.
5. add(0x80); add(0x80) — second add returns __free_hook's slot.
6. edit(that) — write system.
7. add a chunk whose first bytes are "/bin/sh"; del it → system fires.

Every stage verified: the leak's range, the aim's two-alloc, the
write's read-back.
