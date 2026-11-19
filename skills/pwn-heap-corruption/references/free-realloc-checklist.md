# free() inside realloc — the hidden path — checklist

Companion to `free-realloc.md`.

## Checklist

- [ ] A "resize" menu op gives a free+alloc in one call — ordering leverage.
- [ ] realloc(p,0) frees without a visible delete op.
- [ ] realloc moving a chunk leaves a stale copy in the old slot — a UAF
