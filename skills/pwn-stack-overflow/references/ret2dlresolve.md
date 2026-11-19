# ret2dlresolve — resolving a symbol that was never imported

The dynamic linker's lazy-resolution machinery can be tricked into resolving an ARBITRARY symbol name at runtime: craft fake relocation/symbol/string entries, call the resolver stub, and 'system' materializes even though the binary never imported it.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| no useful import but _dl_runtime_resolve exists | fake-resolve possible | ret2dlresolve |
| partial/no RELRO makes the link_map writable | the resolver takes your entries | the chain |
| a controllable relocation index | the fake entries reachable | lay them out |

## Steps

1. Need: a way to put fake Elf64_Rela + Elf64_Sym + a 'system' string in known memory.
2. Call the PLT stub for ANY function with a crafted reloc index pointing at your fake rela.
3. The resolver walks your fake symbol → finds 'system' → binds and calls it.
4. x64 rela layout: r_offset, r_info(sym<<32|type), r_addend — the symbol's st_name points to 'system'.

## Falsifier

Falsifier — no writable place for the fake structures, or the resolver stub isn't reachable: ret2dlresolve can't run.

## Traps

- Full RELRO binds everything at startup — the lazy-resolve path is closed.
- The fake structures must be at a known, readable address — a bss region usually.
- x64 uses JMPREL entries; the index math differs from x86.

## Commands

```bash
readelf -r ./chal
readelf -S ./chal | grep -iE 'plt|got|rela'
```

## Cross-references

`ret2libc.md` · `fgot-overwrite.md`
