# The gadget search — the full method


## The tools (what's present)

    python3 tools/pwn_triage.py ./chal --gadgets   # the essential set
    r2 -A ./chal
    /R pop rdi            # specific
    /Rj pop               # JSON, all pops
    /R syscall            # syscall stubs
    /R leave              # pivots

## The audit

Read each hit's full tail — `pd 4 @ addr` — side effects matter.

## Falsifier

A needed pattern is absent: the chain must express the operation via
a substitute (xor/mov/ret2csu).
