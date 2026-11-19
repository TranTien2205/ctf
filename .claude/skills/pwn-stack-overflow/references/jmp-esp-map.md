# jmp rsp / call reg — the 'execute what's already there' transfer — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| NX off + a jmp esp/call esp gadget | one-transfer exec | the gadget |
| shellcode must live inside the input | where RSP points after ret | jmp esp |
| no known buffer address | RSP is the address | jmp esp |

## Falsifier

Falsifier — NX is on: nothing on the stack executes; jmp esp is moot.
