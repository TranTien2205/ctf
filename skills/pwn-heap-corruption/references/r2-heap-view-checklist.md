# r2 -d heap view — dmh and friends — checklist

Companion to `r2-heap-view.md`.

## Checklist

- [ ] `r2 -d ./chal` — start under the debugger.
- [ ] `dm` — memory maps (find the heap region).
- [ ] `dmh` — heap walk: chunk list, sizes, flags, bin membership.
- [ ] `dmhf` — fastbin/tcache state.
- [ ] `dmhb` / `dmhu` — specific bin inspection.
- [ ] `db <addr>` — break at the vulnerable op; `dc` — continue.
- [ ] `pxq <addr>` — read the chunk words.
