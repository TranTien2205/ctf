# ret2dlresolve — resolving a symbol that was never imported — checklist

The dynamic linker's lazy-resolution machinery can be tricked into resolving an ARBITRARY symbol name at runtime: craft fake relocation/symbol/string entries, call the resolver stub, and 'system' materializes even though the binary never imported it.

## Checklist

- [ ] Need: a way to put fake Elf64_Rela + Elf64_Sym + a 'system' string in known memory.
- [ ] Call the PLT stub for ANY function with a crafted reloc index pointing at your fake rela.
- [ ] The resolver walks your fake symbol → finds 'system' → binds and calls it.
- [ ] x64 rela layout: r_offset, r_info(sym<<32|type), r_addend — the symbol's st_name points to 'system'.

## Abort conditions

- Full RELRO binds everything at startup — the lazy-resolve path is closed.
- The fake structures must be at a known, readable address — a bss region usually.
- x64 uses JMPREL entries; the index math differs from x86.

## Falsifier

Falsifier — no writable place for the fake structures, or the resolver stub isn't reachable: ret2dlresolve can't run.
