# Verifying the chain — the r2 -d walk


Debug the chain before firing remote:

    r2 -d ./chal
    db <the overwrite's landing>
    dc                        # run to the breakpoint
    ds                        # step — watch rip walk the gadgets
    dr                        # check the registers at each step

## The reads

- rip should be your first gadget, then the second, then the call.
- rdi/rsi/rdx should hold your args at the call.
