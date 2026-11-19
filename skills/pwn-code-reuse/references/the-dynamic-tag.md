# The dynamic tags — DT_* for the resolver


The .dynamic section's tags (DT_STRTAB, DT_SYMTAB, DT_JMPREL) hold
the pointers ret2dlresolve needs — read them via readelf -d.

## The offsets

    readelf -d ./chal

The strtab/symtab/jmprel addresses anchor the forged structures.
