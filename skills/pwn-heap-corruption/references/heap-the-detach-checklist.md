# Detached chunks — the inaccessible free — checklist

Companion to `heap-the-detach.md`.

## Checklist

- [ ] unsorted → sorted on the next malloc sweep.
- [ ] fastbin → consolidated on a large request.
- [ ] tcache → stays (no consolidation) — the stable window.
