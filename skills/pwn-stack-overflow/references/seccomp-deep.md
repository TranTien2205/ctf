# Seccomp — the syscall whitelist that shapes the payload — deep

A seccomp filter restricts which syscalls the process may make: open may be banned while openat is allowed, execve banned entirely — the shellcode or syscall-chain must use only allowed calls.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — no seccomp filter and the standard execve path exists: this file doesn't apply.

## Highest-cost traps

- execve banned → no shell, but open+read+write still exfiltrates the flag.
- open banned + openat allowed → the openat(openat_v) variant.
- A filter may also ban read/write on unexpected fds — test the allowed set.

## Commands

```bash
readelf -s ./chal | grep -iE 'seccomp|prctl'
```

## Cross-references

`ret2shellcode.md` · `tools-sc-gen.md`
