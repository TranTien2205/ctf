# free() inside realloc — the hidden path


realloc(p, 0) frees p; realloc(p, s) may free+alloc — the realloc op
is an alloc and a free you might not have counted.

## Exploitation

- A "resize" menu op gives a free+alloc in one call — ordering leverage.
- realloc(p,0) frees without a visible delete op.
- realloc moving a chunk leaves a stale copy in the old slot — a UAF
  through a different door.

## Falsifier

realloc isn't exposed, or it always allocates same-size in place: no
extra primitive.
