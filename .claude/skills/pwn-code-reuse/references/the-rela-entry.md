# The Elf64_Rela — the relocation's shape


A fake relocation entry:

    struct { r_offset; r_info; r_addend }   # 24 bytes

r_info = (sym_index << 32) | type — the index points at your fake
symbol.
