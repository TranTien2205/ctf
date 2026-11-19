# Verifying a gadget — the tail audit


Before using a gadget: read its full tail.

    r2 -A ./chal
    pd 4 @ gadget_addr

Check: does it end in ret? What else does it do — extra pops, memory
writes, jumps? Each side effect must be tolerable.
