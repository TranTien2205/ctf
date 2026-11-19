# tcache is per-thread — the isolation — checklist

Companion to `the-per-thread.md`.

## Checklist

- [ ] Grooming on one thread doesn't affect another's tcache.
- [ ] A worker-thread free in a threaded server is per-worker.
