# ROP basics — code reuse when NX is on — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| NX on + gadgets exist | ROP applies | pwn-code-reuse |
| pop rdi;ret + syscall;ret found | the primitives exist | chain them |
| no good gadget for a step | need a different chain | pivot or multi-stage |

## Falsifier

Falsifier — the gadgets needed don't exist in the binary (or a needed constant can't be loaded): ROP fails; need a leak or a different primitive.
