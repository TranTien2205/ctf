# The argument-offset finder — where your buffer lands — checklist

Every %N$p or %N$n needs the offset N where YOUR input sits as a printf argument. AAAA.%N$p scanning N until 0x41414141 returns is the measurement.

## Checklist

- [ ] Send 'AAAA.%N$p' — printf reads the Nth arg, %p prints it.
- [ ] Scan N upward until 0x41414141 appears — that's your buffer's argument index.
- [ ] x64: the first 6 args are registers (rdi..r9); the stack args start ~N=6 or 7.
- [ ] Once N is known, %N$p reads it, %N$s derefs it, %N$n writes to it.

## Abort conditions

- The offset N is per-call — it shifts if the call site changes.
- x86: all args on the stack, so N starts low; x64: the register args come first.
- The planted pointer for %s must land where a %N$s arg reads it.

## Falsifier

Falsifier — your input never appears as a %N$p value at any N: the buffer isn't a printf argument; the primitive can't reach it.
