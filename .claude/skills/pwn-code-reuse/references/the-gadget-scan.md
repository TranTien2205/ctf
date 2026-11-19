# Scanning for gadgets — the r2 way


ROPgadget/ropper are absent — the search is:

    python3 tools/pwn_triage.py ./chal --gadgets   # the essentials
    r2 -A ./chal
    /R pop rdi            # specific pattern
    /Rj pop               # all pops, JSON
    /R syscall            # syscall gadgets

## The output

Each hit gives an address (PIE: offset) and the instruction tail —
verify the tail ends in ret/call/jmp correctly.

## Falsifier

The needed gadget pattern is absent: the chain must express the
operation differently.
