# When consolidation fires — the trigger map


Consolidation doesn't run on every free — it runs on: free() into a
consolidating bin (large chunks), a malloc too big for bins, explicit
malloc_consolidate, and the top-merge.

## The triggers

- free() of a non-fastbin/tcache chunk adjacent to a free one.
- _int_malloc on an unsorted sweep.
- malloc_consolidate called on large requests.
- free() of the chunk just below top (top-merge).

## Exploitation reading

Schedule the trigger AFTER the corruption is in place — a premature
consolidate merges clean state, not your forged state.

## Falsifier

The needed trigger isn't reachable by the program's ops: the merge
never fires.
