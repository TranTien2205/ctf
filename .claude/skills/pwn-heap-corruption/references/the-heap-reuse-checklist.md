# The reuse window — when a freed chunk returns — checklist

Companion to `the-heap-reuse.md`.

## Checklist

- [ ] Long-running service: the window can be many ops.
- [ ] The stale data decays as bin ops overwrite the chunk's links — the
