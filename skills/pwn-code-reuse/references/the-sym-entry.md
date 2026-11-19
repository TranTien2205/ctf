# The Elf64_Sym — the symbol's shape


A fake symbol entry:

    struct { st_name; st_info; st_other; st_shndx; st_value; st_size }

st_name = the offset into strtab where your function's name string
sits — the resolver reads it to find the target.
