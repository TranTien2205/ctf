# The fake frame — a hand-built stack


A planted buffer that LOOKS like a stack frame: saved rbp + saved rip
+ locals — a pivot into it lets leave;ret resume a fake frame.

## The use

Combined with leave;ret: pivot to the fake frame, the epilogue's
leave;ret then reads your forged continuation.
