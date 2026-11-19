# Remote vs local — socket protocol vs process — deep

Remote pwn is a socket conversation: read the prompt, send the payload, read the response. The discipline is netcat/python-socket, not pwntools here.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the remote service doesn't fork per connection and one crash kills it for everyone: exploit carefully — every probe is shared state.

## Highest-cost traps

- Forking servers give a fresh canary/ASLR per connection ONLY if exec'd; forked children share it.
- Send the payload bytes then a newline — some reads block until the newline.
- Raw socket with `python3 -c` or `nc` heredoc works; pwntools is absent here.

## Commands

```bash
nc <host> <port>
python3 -c "import socket;s=socket.socket();s.connect(('<h>',<p>));s.send(b'A'*40);print(s.recv(1024))"
```

## Cross-references

`sendline-protocols.md` · `canary-bypass.md`
