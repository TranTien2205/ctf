# ret2shellcode — when NX is off — checklist

NX off means the stack (or a buffer) is executable: write your shellcode, jump to it. tools/sc_gen.py emits tested stubs — no pwntools needed.

## Checklist

- [ ] Confirm NX off in pwn_triage output.
- [ ] python3 tools/sc_gen.py execve64 --raw — the tested execve('/bin/sh') stub.
- [ ] Find a writable+executable region (stack, .data, mmap'd).
- [ ] Payload: pad + p64(buffer_addr) + shellcode at that address.

## Abort conditions

- Byte filters: reads stopping at \x00\x0a\x0d\x20 kill shellcode with those bytes — sc_gen reports which the stub contains.
- Stack addresses are ASLR'd — you need the buffer's real address, usually from a leak or a jmp rsp gadget.
- cat64 reads the flag file; rev64 gives a reverse shell (--host/--port).

## Falsifier

Falsifier — NX is on: no shellcode executes regardless of control; the chain must be code-reuse.
