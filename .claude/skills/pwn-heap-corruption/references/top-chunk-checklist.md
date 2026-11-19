# The top chunk — the wilderness — checklist

Companion to `top-chunk.md`.

## Checklist

- [ ] Top sits at the heap's end; its size = remaining space.
- [ ] A huge fake top size makes the next malloc "allocate" past the heap —
- [ ] Conserving the top: small frees can merge upward into it (clearing
