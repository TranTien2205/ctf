# The sendline protocol — remote service shape — deep

A remote pwn service reads a line, processes it, responds. The payload must survive the transport: newlines, length limits, and the service's framing.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the service's read bound stops before your offset: the payload can't reach the saved state at this size.

## Highest-cost traps

- A length-prefixed protocol bounds the payload — the offset must fit inside it.
- Newline-terminated reads need the trailing '\n'.
- Some services read a fixed number of bytes regardless of newlines — send exactly that many.

## Commands

```bash
nc <host> <port>
python3 -c "import socket;s=socket.socket();s.connect(('<h>',<p>));s.send(b'...')"   # stdlib socket
```

## Cross-references

`remote-vs-local.md`
