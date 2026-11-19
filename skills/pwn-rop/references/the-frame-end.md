# The frame's end — the epilogue's effect


The epilogue: `leave; ret` — rsp = rbp+8 (past saved rip) — the
first chain entry is read there.

## The accounting

Everything before saved-rip is padding; the chain begins at the
saved-rip slot exactly.
