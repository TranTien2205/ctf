# Stack pivot — when the writable area is too small — case catalogue

The buffer is too small for the chain, or the stack isn't where you want it. Pivot: point RSP elsewhere with a 'leave; ret' or 'xchg rsp, rXx' gadget.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | controlled buffer too small for the chain | pivot | leave;ret |
| 2 | a large controlled region elsewhere (heap, bss) | target for RSP | xchg/add rsp |
| 3 | rbp is attacker-influenced | leave;ret pivots | the classic move |

## Falsifier

Falsifier — no controllable RBP and no xchg/add-rsp gadget: no pivot exists.
