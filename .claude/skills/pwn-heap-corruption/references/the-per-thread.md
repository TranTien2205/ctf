# tcache is per-thread — the isolation


Each thread has its own tcache — a chunk freed by thread A goes to A's
tcache, not B's: cross-thread frees land differently.

## Consequence

- Grooming on one thread doesn't affect another's tcache.
- A worker-thread free in a threaded server is per-worker.

## Falsifier

Single-threaded service: the note is moot.
