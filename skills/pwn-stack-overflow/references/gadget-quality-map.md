# Gadget quality — which gadgets are usable and which aren't — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| pop rdi; ret | clean, one arg | use it |
| pop rdi; pop rbp; ret | consumes 2 slots | pad the extra |
| a gadget with side effects (call/add) | alters state | check the effect |
| an indirect gadget (jmp [reg]) | needs a register set | harder |

## Falsifier

Falsifier — the only available gadget for a needed register has a side-effect that breaks the chain: find a different chain shape.
