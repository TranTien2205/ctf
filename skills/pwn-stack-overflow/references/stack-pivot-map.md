# Stack pivot — when the writable area is too small — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| controlled buffer too small for the chain | pivot | leave;ret |
| a large controlled region elsewhere (heap, bss) | target for RSP | xchg/add rsp |
| rbp is attacker-influenced | leave;ret pivots | the classic move |

## Falsifier

Falsifier — no controllable RBP and no xchg/add-rsp gadget: no pivot exists.
