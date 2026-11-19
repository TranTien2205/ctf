# r2 -d heap view — dmh and friends


gdb is absent; `r2 -d ./chal` is the runtime heap view.

## The commands

- `r2 -d ./chal` — start under the debugger.
- `dm` — memory maps (find the heap region).
- `dmh` — heap walk: chunk list, sizes, flags, bin membership.
- `dmhf` — fastbin/tcache state.
- `dmhb` / `dmhu` — specific bin inspection.
- `db <addr>` — break at the vulnerable op; `dc` — continue.
- `pxq <addr>` — read the chunk words.

## The discipline

Set the breakpoint BEFORE the corruption, dmh the clean state, step
past, dmh again — the diff shows exactly what your corruption did.

## Falsifier

r2 isn't available in the environment (checked with `which r2`): fall
back to observable behavior — alloc addresses and crash messages.
