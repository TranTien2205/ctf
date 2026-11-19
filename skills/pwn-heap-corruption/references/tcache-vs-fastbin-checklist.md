# tcache vs fastbin — the routing decision — checklist

Companion to `tcache-vs-fastbin.md`.

## Checklist

- [ ] tcache[i] < 7 → the free goes to tcache.
- [ ] tcache[i] == 7 → the free falls to fastbin (if small enough) or
- [ ] Want fastbin? Burn 7 same-size frees first.
- [ ] Want tcache? Keep counts low.
- [ ] The routing is per-size — different sizes route differently
