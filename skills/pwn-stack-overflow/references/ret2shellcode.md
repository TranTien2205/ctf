# ret2shellcode — when NX is off

NX off means the stack (or a buffer) is executable: write your shellcode, jump to it. tools/sc_gen.py emits tested stubs — no pwntools needed.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| NX disabled in protections | shellcode executable | write + jump |
| a writable+executable region | code home | point RIP there |
| SC_GEN stubs: execve64/execve86/cat64/rev64 | tested shellcode | --raw for hex |

## Steps

1. Confirm NX off in pwn_triage output.
2. python3 tools/sc_gen.py execve64 --raw — the tested execve('/bin/sh') stub.
3. Find a writable+executable region (stack, .data, mmap'd).
4. Payload: pad + p64(buffer_addr) + shellcode at that address.

## Falsifier

Falsifier — NX is on: no shellcode executes regardless of control; the chain must be code-reuse.

## Traps

- Byte filters: reads stopping at \x00\x0a\x0d\x20 kill shellcode with those bytes — sc_gen reports which the stub contains.
- Stack addresses are ASLR'd — you need the buffer's real address, usually from a leak or a jmp rsp gadget.
- cat64 reads the flag file; rev64 gives a reverse shell (--host/--port).

## Commands

```bash
python3 tools/sc_gen.py execve64 --raw
python3 tools/sc_gen.py cat64 --path /flag --raw
python3 tools/sc_gen.py --selftest
```

## Cross-references

`tools-sc-gen.md` · `protection-modes.md` · `bad-chars.md`
