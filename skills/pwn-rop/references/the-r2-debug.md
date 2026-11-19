# The r2 -d session — the full debug walk


    r2 -d ./chal
    db 0x<the_return_site>      # or break at a gadget
    dc
    pxq @ rsp                   # the chain as laid out
    ds                          # step: rip should be gadget 1
    dr rip rdi rsi rdx          # the state
    ds                          # gadget 2 ...
    ds                          # the call

Each step is verifiable — a divergence shows the failing qword.
