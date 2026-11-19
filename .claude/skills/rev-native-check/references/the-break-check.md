# Breaking at the check — the dynamic read


gdb is absent — r2 -d is the debugger:

    r2 -d ./chal
    db <the_cmp_addr>
    dc
    dr rdi rsi              # strcmp's args
    px @ rsi                # or the memory operand

The compare's two operands at the break ARE the answer — the correct
input is usually sitting in one.
