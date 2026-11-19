# Chain verification — landing it step by step


Don't build the whole chain and test it once — verify each stage: does
the first gadget execute? does the call site run? does the output appear?

## The ladder

1. The offset — cyclic + fault: RIP holds your bytes.
2. The first gadget — a ret/pop that runs.
3. The call site — the function/syscall executes (visible side-effect).
4. The output — the flag or the shell.

## The discipline

Each stage's failure points at a specific boundary (alignment, arg,
bad-byte) — fix the stage, don't rebuild the whole chain.
