# Preloaded args — when registers are already set


Sometimes the needed arg is already in a register at the call point —
check r2 -d: rdi may already point at your buffer — the pop is
unneeded.

## The free win

Read the register state at the call site before assuming you must
set it.
