# ret2func — calling a fixed address


Calls a function whose address you know — a win function, a PLT
entry's target under non-PIE, a libc function after a leak.

    python3 tools/rop_chain.py ./chal ret2func --func 0x401160 --arg 0x404060 --arg2 0 --arg3 0

## The packing

    pop rdi ; arg
    pop rsi ; arg2     # if --arg2 given
    pop rdx ; arg3     # if --arg3 given
    ret                # if alignment needs it
    func

## The falsifier

A needed pop gadget is absent — the tool reports which.
