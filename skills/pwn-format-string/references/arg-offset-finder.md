# The argument-offset finder — where your buffer lands

Every %N$p or %N$n needs the offset N where YOUR input sits as a printf argument. AAAA.%N$p scanning N until 0x41414141 returns is the measurement.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| a %p leak shows your bytes | the offset is findable | scan N |
| you plant a pointer for %s/%n | need its argument index | the offset |
| x64 first args in regs | N ≥ ~6 for the stack | the stack args |

## Steps

1. Send 'AAAA.%N$p' — printf reads the Nth arg, %p prints it.
2. Scan N upward until 0x41414141 appears — that's your buffer's argument index.
3. x64: the first 6 args are registers (rdi..r9); the stack args start ~N=6 or 7.
4. Once N is known, %N$p reads it, %N$s derefs it, %N$n writes to it.

## Falsifier

Falsifier — your input never appears as a %N$p value at any N: the buffer isn't a printf argument; the primitive can't reach it.

## Traps

- The offset N is per-call — it shifts if the call site changes.
- x86: all args on the stack, so N starts low; x64: the register args come first.
- The planted pointer for %s must land where a %N$s arg reads it.

## Commands

```bash
# send 'AAAA.%1$p'..'AAAA.%20$p' and find which prints 0x41414141
```

## Cross-references

`primitive-matrix.md` · `the-stack-args.md`
