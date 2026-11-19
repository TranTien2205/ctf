# The rtld route — _dl_runtime_resolve


The lazy-binding resolver: plt[0] pushes a reloc index and jumps to
the resolver — ret2dlresolve forges that call.

## The mechanism

    push reloc_index
    jmp plt[0]                # → _dl_runtime_resolve(link_map, idx)

The resolver reads .rela.plt[reloc_index] → r_info → sym index →
.dynsym[sym] → st_name → .dynstr[st_name] — the name string decides
the resolved function.

## The forge

Put the reloc index + the structures where the walk reads your fake
ones — the resolved "symbol" is your chosen libc function.
