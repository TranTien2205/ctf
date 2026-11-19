# Verifying the chain — the r2 -d walk


Debug the chain under r2 -d:

    r2 -d ./chal
    db <the ret-addr overwrite point>
    dc
    ds         # step each ret — watch rip walk the chain
    dr         # the registers at each step

Each gadget's effect is observable — a divergence shows the bad
gadget.
