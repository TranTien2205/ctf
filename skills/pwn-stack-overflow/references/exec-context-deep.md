# Execution context — what the payload runs as — deep

The exploit runs inside the process's context: its fds, its privileges, its seccomp. The flag-read or shell inherits that context.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the service's context can't reach the flag file (permissions, chroot, seccomp): the flag-read fails even if code-exec succeeds.

## Highest-cost traps

- cat64's --path must match where the flag actually is.
- A socket service's fd 0/1 is the socket — rev64 connects OUT, cat64 writes to the socket.
- A setuid binary vs a network service have different exec-contexts.

## Commands

```bash
python3 tools/sc_gen.py cat64 --path /flag --raw
```

## Cross-references

`tools-sc-gen.md` · `seccomp.md`
