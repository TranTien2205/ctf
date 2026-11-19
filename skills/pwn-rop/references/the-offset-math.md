# Offset math — base + offset


    libc_base  = leak - the_symbol_offset
    system     = libc_base + system_offset
    binsh      = libc_base + binsh_offset
    gadget     = binary_base + gadget_offset   (PIE)

The offsets come from the shipped file (readelf -s) or the
identified build; the bases come from the leaks.
