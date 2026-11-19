# jmp rsp / call reg — the 'execute what's already there' transfer — case catalogue

Instead of writing shellcode past the saved RIP, a 'jmp esp'/'call esp' gadget jumps back INTO your own input on the stack — shellcode travels in the same bytes as the smash.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | NX off + a jmp esp/call esp gadget | one-transfer exec | the gadget |
| 2 | shellcode must live inside the input | where RSP points after ret | jmp esp |
| 3 | no known buffer address | RSP is the address | jmp esp |

## Falsifier

Falsifier — NX is on: nothing on the stack executes; jmp esp is moot.
