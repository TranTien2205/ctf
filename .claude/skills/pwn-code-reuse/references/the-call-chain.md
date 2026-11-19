# The call-chain — the sequence as calls


A chain read as calls: each gadget+arg pair is a "call" —

    set_rdi(arg0) ; set_rsi(arg1) ; call(func) ; ret_or_exit

The mental model: the stack is a bytecode program, ret is the
instruction pointer.
