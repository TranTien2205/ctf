# The bck->fd check — unsorted's consistency


On the unsorted-bin removal path, `victim->bck->fd` must equal victim —
corrupting bk alone fails the check unless the pointed-to slot's fd
field agrees.

## The requirement

bk = target - 0x10 works only if target+0x00 already holds `victim`
(or you can make it so) — i.e., the target must already contain a
self-referential pointer.

## Falsifier

The target can't be made self-consistent: unsorted-bin writes are
closed — a different bin's machinery must deliver.
