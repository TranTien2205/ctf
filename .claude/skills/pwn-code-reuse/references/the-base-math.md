# Base arithmetic — leak to addresses


    binary_base = leaked_code_ptr - code_ptr_offset
    libc_base   = leaked_libc_ptr - the_symbol_offset
    gadget_addr = binary_base + gadget_offset

Every chain entry derives from a base + offset — the leak's job is
the base.
