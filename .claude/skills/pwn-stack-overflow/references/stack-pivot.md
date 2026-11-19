# Stack pivot — when the writable area is too small

The buffer is too small for the chain, or the stack isn't where you want it. Pivot: point RSP elsewhere with a 'leave; ret' or 'xchg rsp, rXx' gadget.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| controlled buffer too small for the chain | pivot | leave;ret |
| a large controlled region elsewhere (heap, bss) | target for RSP | xchg/add rsp |
| rbp is attacker-influenced | leave;ret pivots | the classic move |

## Steps

1. Find the pivot gadget: 'leave; ret' (RSP:=RBP, RBP pop, ret) — if you control RBP, you control RSP.
2. Set RBP to the address of your staged ROP buffer (elsewhere in memory).
3. First-stage: overflow to set RBP to the staged buffer, return to 'leave;ret'.
4. Second-stage buffer holds the full ROP chain.

## Falsifier

Falsifier — no controllable RBP and no xchg/add-rsp gadget: no pivot exists.

## Traps

- 'leave; ret' uses RBP — you need RBP control, usually from the same smash.
- The staged buffer must be readable/writable and known-address — a bss or heap region.
- Two-stage attacks need two writes or one write to the staged area.

## Commands

```bash
r2 -A ./chal && /R leave
```

## Cross-references

`rop-basics.md` · `fgot-overwrite.md`
