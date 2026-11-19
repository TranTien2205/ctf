# Hunting xor — the zeroing gadget


    /R xor

`xor rX, rX; ret` zeroes a register — the substitute for a missing
pop when the value is 0.

## The use

execve's rsi/rdx = 0 — an xor gadget replaces the pops.
