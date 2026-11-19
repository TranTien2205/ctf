# A complete modern chain — 2.32+ end to end


The full modern recipe, every stage:

1. UAF: free an object; the pointer dangles.
2. Exhaust tcache for a bigger size; free a victim → unsorted.
3. Read the victim's fd through a dangling alias → libc leak.
4. Read a mangled tcache fd → de-mangle with the known chunk pos →
   heap base.
5. Write a chunk's fd = (pos>>12) ^ &__free_hook → aim.
6. Two allocs → second returns __free_hook's slot.
7. Write system into it; free a "/bin/sh" chunk → shell.

Every stage's falsifier: leak absent → blind; no UAF → different entry;
hooks gone → FSOP instead.
