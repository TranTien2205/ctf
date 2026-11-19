# The old unlink — pre-2.30 FD/BK write


Classic unlink: corrupt a free chunk's fd/bk so `chunk->fd->bk =
chunk->bk` writes one pointer into another — an arbitrary 4/8-byte
write. Heavily checked since 2.30.

## The write

    FD = victim->fd; BK = victim->bk;
    FD->bk = BK;   // writes BK into FD+0x18 (x64)
    BK->fd = FD;   // writes FD into BK+0x10

With fd = &ptr-0x18 and bk = target, unlink writes `ptr` into target —
a "pointer writes itself" primitive.

## Version gate

glibc >= 2.30 hardens unlink: `chunk->fd->bk == chunk` and
`chunk->bk->fd == chunk` are verified — the fake links fail unless both
are consistent, which usually requires a full fake chunk.

## Falsifier

The corruption can't satisfy `fd->bk == chunk && bk->fd == chunk`:
unlink aborts — closed on modern glibc.
