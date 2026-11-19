# The arg window vs raw stack — what %N$p actually sees


%N$p reads the Nth vararg — which on x64 for N>6 is a stack slot ABOVE the
callee's frame: it sees the caller's stack args and whatever sits there,
including your input buffer.

## Steps

1. The declared varargs end at the call's arity — beyond that, %N$p reads
   raw stack memory.
2. Your input buffer may BE a stack arg or stack memory at higher N.
3. Higher N reaches the caller's saved registers and return addresses.

## Falsifier

None; the window just gets deeper — reading past the varargs isn't an
error, it walks the stack. That's how the canary/PIE leaks happen.
