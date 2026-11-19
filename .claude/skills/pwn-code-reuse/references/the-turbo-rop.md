# Turbo-rop — precomputed chains


When the chain shape is fixed (same gadget set every run), precompute
the offset skeleton and fill only the runtime addresses — speed when
the server is short-lived.

## The skeleton

    pops + args + call — with placeholders for the base.

Fill base + offsets per run; the skeleton is constant.

## Falsifier

Gadget addresses change per run (PIE re-randomized): every run
recomputes — the skeleton only holds offsets, not addresses.
