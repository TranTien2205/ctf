# ret2dlresolve — the no-leak call


Forge the relocation structures so _dl_runtime_resolve "resolves" to
a chosen libc function — a call with no libc leak, on lazy-binding
targets.

## The structure

A fake Elf64_Rela + Elf64_Sym + the symbol's name string in writable
memory; the resolver's walk reads them.

## Falsifier

Full RELRO — no lazy binding; or no writable region for the fakes.
