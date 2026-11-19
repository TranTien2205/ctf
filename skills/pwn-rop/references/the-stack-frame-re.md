# The frame revisit — the epilogue's role


The function's epilogue (`leave; ret` or `pop rbp; ret`) consumes the
saved regs before the chain starts — the chain's first slot is read
by that final ret.
