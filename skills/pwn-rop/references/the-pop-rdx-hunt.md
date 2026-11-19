# Hunting pop rdx — the scarce arg


The scarcest of the three arg pops — many binaries lack a clean one:

## The substitutes

- `pop rdx; pop rXX; ret` — a paired pop.
- `xor edx, edx` gadgets — for a 0 arg.
- ret2csu's `mov rdx, r15` path.
- A `mov rdx, rXX` gadget when a register holds the value.

## Falsifier

No path to rdx: execve's envp arg (or any 3-arg call) is unreachable —
choose a 1-arg ending or ret2csu.
