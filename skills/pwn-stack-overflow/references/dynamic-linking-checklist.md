# Dynamic linking internals — how PLT/GOT really work — checklist

The PLT/GOT mechanism is the ret2plt/ret2libc/GOT-overwrite foundation: understand it and those chains write themselves.

## Checklist

- [ ] First call: PLT stub jumps to GOT[x], which points back to the resolver stub → _dl_runtime_resolve writes the real addr into GOT[x].
- [ ] Later calls: PLT jumps to GOT[x] = the real libc addr directly.
- [ ] Under lazy binding, an uncalled function's GOT[x] is the PLT address — not the libc addr.
- [ ] ret2plt calls the PLT stub — it resolves and calls the real function.

## Abort conditions

- A 'puts(GOT[puts])' leak only shows the libc addr AFTER puts was called once — else it's the PLT addr.
- Full RELRO pre-resolves everything — GOT is readonly, no lazy path.
- The resolver is _dl_runtime_resolve — the ret2dlresolve target.

## Falsifier

Falsifier — full RELRO binds everything at startup: no lazy path exists; GOT[x] is already the real addr.
