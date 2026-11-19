# The offset math — base + offset arithmetic


    gadget_addr = base + gadget_offset
    func_addr   = base + func_offset        (PIE)
    libc_func   = libc_base + symbol_offset (dynamic)

The offsets come from the binary's disassembly (r2 -A); the bases
come from leaks.
