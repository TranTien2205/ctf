# ret2dlresolve — the forged resolver call


Forge the relocation structures so _dl_runtime_resolve "resolves"
any libc function — a call with no libc leak, on lazy-binding
targets.

## The structures

A fake Elf64_Rela + Elf64_Sym + the name string in writable memory —
the resolver's walk reads them.

## Falsifier

Full RELRO or no writable region for the fakes.
