# Multi-step chains — the compositions

## leak → write → redirect → flag
1. %p run: canary + base leaked.
2. %n to GOT/ret-addr: the chain's first address written.
3. The call/return redirects → the chain runs → flag.

## fmtstr-leak → stack-smash → flag
1. %p leaks canary + PIE base.
2. The smash preserves the canary, uses base-relative addrs.
3. The smash runs → flag.

## byte-wise-write → GOT → flag
1. %hhn writes each byte of system into puts's GOT slot.
2. Next puts() call → system().
