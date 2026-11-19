# The strcmp shape — the literal compare


A strcmp/memcmp against a constant: the answer is in .rodata — the
literal string at the second arg.

## The read

    pdf @ <the_check_func>
    # the second arg's address → the constant:
    ps @ <the_const_addr>
    # or strings -t x and the xref's target

## The trap

A strcmp against a BUILT value (not a constant): the constant is
assembled at run time — the build instructions are the answer.
