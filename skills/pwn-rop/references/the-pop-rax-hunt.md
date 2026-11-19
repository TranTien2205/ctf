# Hunting pop rax — the syscall number


The syscall number's setter — needed for every syscall chain:

    /R pop rax

## The substitutes

- `xor eax, eax; ...; add/inc eax` — building to the number.
- A `mov eax, ...` gadget.
- ret2csu doesn't help — rax isn't in its set.

## Falsifier

No rax path at all: the syscall route is closed — ret2libc.
