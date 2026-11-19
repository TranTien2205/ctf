# ROP basics — code reuse when NX is on — case catalogue

Return-oriented programming: chain existing code fragments ending in 'ret' to do work without injecting code. pwn-code-reuse is the owning class; this file is the bridge.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | NX on + gadgets exist | ROP applies | pwn-code-reuse |
| 2 | pop rdi;ret + syscall;ret found | the primitives exist | chain them |
| 3 | no good gadget for a step | need a different chain | pivot or multi-stage |

## Falsifier

Falsifier — the gadgets needed don't exist in the binary (or a needed constant can't be loaded): ROP fails; need a leak or a different primitive.
