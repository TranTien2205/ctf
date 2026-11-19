# Gadget quality — which gadgets are usable and which aren't — case catalogue

Not all gadgets are equal: a 'pop rdi; ret' is clean; 'pop rdi; pop rbp; ret' consumes an extra slot; a conditional gadget needs the right flags.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | pop rdi; ret | clean, one arg | use it |
| 2 | pop rdi; pop rbp; ret | consumes 2 slots | pad the extra |
| 3 | a gadget with side effects (call/add) | alters state | check the effect |
| 4 | an indirect gadget (jmp [reg]) | needs a register set | harder |

## Falsifier

Falsifier — the only available gadget for a needed register has a side-effect that breaks the chain: find a different chain shape.
