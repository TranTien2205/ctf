# The chain builder — rop_chain.py


The local assembler: emits the packed qwords for the three common
chain shapes — no pwntools needed.

## The three modes

    python3 tools/rop_chain.py ./chal ret2func --func 0x401160 --arg 0x404060
    python3 tools/rop_chain.py ./chal syscall --num 59 --arg 0x404030
    python3 tools/rop_chain.py ./chal ret2plt --plt puts --arg 0x404018

## What it does

- Finds the pop gadgets itself in the binary.
- Packs `pop rdi/rsi/rdx` chains in argument order.
- Inserts a bare `ret` when the qword count leaves rsp misaligned.
- ret2plt resolves the stub itself: walks .rela.plt to the symbol's
  GOT slot, then decodes the `ff 25` stubs until one references it.

## The failure mode

A missing gadget or an undecodable stub is REPORTED, never faked —
the tool's "cannot" is a real falsifier.

## Selftest

    python3 tools/rop_chain.py --selftest
