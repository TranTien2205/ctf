# Walking .rela.plt — the resolution entries


Each Elf64_Rela: {r_offset = the GOT slot, r_info = sym<<32|type,
r_addend} — the resolver's input.

## The use

- ret2plt reads it to map symbols to slots.
- ret2dlresolve forges it — the fake relocation the resolver reads.
