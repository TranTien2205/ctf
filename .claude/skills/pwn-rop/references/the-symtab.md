# The symbol tables — .symtab vs .dynsym


- .dynsym: dynamic symbols — the imports/exports.
- .symtab: the full table (if not stripped).

## The reads

    readelf -s ./chal         # both tables
    nm -D ./chal              # dynamic only
    python3 tools/elf_info.py ./chal --symbols-only

## Stripped

No .symtab: afl and the imports still give the call surface.
