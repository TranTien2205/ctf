# The minimal scan — essential gadgets only


The essential gadget set for a system() chain:

- pop rdi; ret — the arg.
- ret — alignment.
- The call target (system's address).

That's the whole chain: 3 entries + the padding — most real chains
reduce to this plus a leak stage.
