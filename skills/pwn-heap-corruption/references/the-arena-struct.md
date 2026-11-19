# The arena — malloc_state and its members


malloc_state (the arena) holds: mutex, flags, the fastbinsY array,
top pointer, last_remainder, the bins[] array, binmap. It lives in libc
(main arena) or at the heap's start (thread arenas).

## The interesting members

- fastbinsY[NFASTBINS] — the fastbin heads.
- bins[] — unsorted + small + large bin heads (the leak's target).
- top — the wilderness pointer.
- next — the arena chain.

## Exploiting the arena

Corrupting arena members (rare — needs libc-adjacent write) redirects
bin heads: bins[] aiming gives alloc-from-arbitrary.

## Falsifier

The arena isn't writable (it's in libc's data — needs an arbitrary
write already): the arena is a target only post-primitive.
