# The tcache key — 2.29+ double-free detection — checklist

Companion to `tcache-key.md`.

## Checklist

- [ ] Overwrite the key field after the free (UAF write) then free again —
- [ ] Or zero the key via an overflow of the freed chunk's tail.
- [ ] Or free through a different bin path (fastbin where the key isn't
- [ ] Or corrupt `counts[]` in tcache_perthread_struct.
