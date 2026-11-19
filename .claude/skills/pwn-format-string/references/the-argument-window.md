# The argument window — the reachable N range


Your input and the stack args occupy a window of argument positions:
too-low N are registers, too-high N are out of reach. The reachable
window is where your input/pointer can sit.

## The window

- x64: N≥6-ish for stack args.
- Your input sits at some N in the window.
- Very high N may read beyond the mapped stack — a crash.

## The measure

The AAAA.%N$p sweep maps the window — find where your bytes land.
