# The reuse window — when a freed chunk returns


A freed chunk returns on the next same-size alloc (tcache LIFO) — the
window between free and realloc is where the stale data lives.

## The timing

- Long-running service: the window can be many ops.
- The stale data decays as bin ops overwrite the chunk's links — the
  usable window is until the next free of the same size.

## Falsifier

Nothing reads the stale window: the data is unreachable.
