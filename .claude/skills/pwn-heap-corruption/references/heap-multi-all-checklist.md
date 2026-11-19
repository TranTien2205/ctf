# Multi-arena vs single — threaded services — checklist

Companion to `heap-multi-all.md`.

## Checklist

- [ ] Grooming must know which thread/arena the corruption lives in.
- [ ] Cross-arena techniques (house of mind) need the fake arena setup.
- [ ] The tcache is per-THREAD — thread-local bins.
