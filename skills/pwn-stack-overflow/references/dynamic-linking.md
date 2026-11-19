# Dynamic linking internals — how PLT/GOT really work

The PLT/GOT mechanism is the ret2plt/ret2libc/GOT-overwrite foundation: understand it and those chains write themselves.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a call to func@plt | lazy-bind via resolver | the PLT stub |
| GOT holds the resolved addr | the lookup table | overwrite it |
| first call resolves then caches | binding on demand | the lazy path |

## Steps

1. First call: PLT stub jumps to GOT[x], which points back to the resolver stub → _dl_runtime_resolve writes the real addr into GOT[x].
2. Later calls: PLT jumps to GOT[x] = the real libc addr directly.
3. Under lazy binding, an uncalled function's GOT[x] is the PLT address — not the libc addr.
4. ret2plt calls the PLT stub — it resolves and calls the real function.

## Falsifier

Falsifier — full RELRO binds everything at startup: no lazy path exists; GOT[x] is already the real addr.

## Traps

- A 'puts(GOT[puts])' leak only shows the libc addr AFTER puts was called once — else it's the PLT addr.
- Full RELRO pre-resolves everything — GOT is readonly, no lazy path.
- The resolver is _dl_runtime_resolve — the ret2dlresolve target.

## Commands

```bash
readelf -r ./chal
objdump -d ./chal | grep -A3 plt
```

## Cross-references

`ret2plt.md` · `ret2libc.md` · `ret2dlresolve.md`
