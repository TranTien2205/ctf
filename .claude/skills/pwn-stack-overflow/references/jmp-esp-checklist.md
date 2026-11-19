# jmp rsp / call reg — the 'execute what's already there' transfer — checklist

Instead of writing shellcode past the saved RIP, a 'jmp esp'/'call esp' gadget jumps back INTO your own input on the stack — shellcode travels in the same bytes as the smash.

## Checklist

- [ ] Confirm NX off.
- [ ] Find jmp esp or call esp: r2 -A && /R jmp esp (or the pwn_triage gadget list).
- [ ] Chain: pad + p64(jmp_esp) + shellcode — ret lands on jmp esp, which jumps into your shellcode.
- [ ] The shellcode sits right after the overwritten return address.

## Abort conditions

- x64: jmp rsp (not esp); the gadget name follows the register width.
- The shellcode follows the return address — no separate buffer needed.
- Bad bytes in the shellcode still matter — match the read's filter.

## Falsifier

Falsifier — NX is on: nothing on the stack executes; jmp esp is moot.
