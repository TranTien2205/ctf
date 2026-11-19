# Stack pivot — when the writable area is too small — checklist

The buffer is too small for the chain, or the stack isn't where you want it. Pivot: point RSP elsewhere with a 'leave; ret' or 'xchg rsp, rXx' gadget.

## Checklist

- [ ] Find the pivot gadget: 'leave; ret' (RSP:=RBP, RBP pop, ret) — if you control RBP, you control RSP.
- [ ] Set RBP to the address of your staged ROP buffer (elsewhere in memory).
- [ ] First-stage: overflow to set RBP to the staged buffer, return to 'leave;ret'.
- [ ] Second-stage buffer holds the full ROP chain.

## Abort conditions

- 'leave; ret' uses RBP — you need RBP control, usually from the same smash.
- The staged buffer must be readable/writable and known-address — a bss or heap region.
- Two-stage attacks need two writes or one write to the staged area.

## Falsifier

Falsifier — no controllable RBP and no xchg/add-rsp gadget: no pivot exists.
