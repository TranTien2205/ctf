# jmp rsp / call reg — the 'execute what's already there' transfer

Instead of writing shellcode past the saved RIP, a 'jmp esp'/'call esp' gadget jumps back INTO your own input on the stack — shellcode travels in the same bytes as the smash.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| NX off + a jmp esp/call esp gadget | one-transfer exec | the gadget |
| shellcode must live inside the input | where RSP points after ret | jmp esp |
| no known buffer address | RSP is the address | jmp esp |

## Steps

1. Confirm NX off.
2. Find jmp esp or call esp: r2 -A && /R jmp esp (or the pwn_triage gadget list).
3. Chain: pad + p64(jmp_esp) + shellcode — ret lands on jmp esp, which jumps into your shellcode.
4. The shellcode sits right after the overwritten return address.

## Falsifier

Falsifier — NX is on: nothing on the stack executes; jmp esp is moot.

## Traps

- x64: jmp rsp (not esp); the gadget name follows the register width.
- The shellcode follows the return address — no separate buffer needed.
- Bad bytes in the shellcode still matter — match the read's filter.

## Commands

```bash
r2 -A ./chal && /R jmp
python3 tools/pwn_triage.py ./chal --gadgets
```

## Cross-references

`ret2shellcode.md` · `rop-basics.md`
