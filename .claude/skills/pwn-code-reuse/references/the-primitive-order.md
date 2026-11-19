# Primitive order — the chain's dependencies


The ROP chain's prerequisites stack:

    IP-control → leak → base computation → gadget addresses →
    args set → call → ending

Each layer needs the one before it — a missing layer is a falsifier,
not a speedup.
