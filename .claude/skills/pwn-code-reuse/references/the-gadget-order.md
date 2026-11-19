# The gadget order — side-effect awareness


Gadgets execute in sequence — a gadget's side effects (memory writes,
register clobbers, jumps) propagate: audit each one's full tail.

## The audit

    r2 -A ./chal
    pd 3 @ gadget_addr    # see the full instruction sequence

Prefer minimal-side-effect gadgets; avoid gadgets whose side effects
clobber state a later gadget needs.
