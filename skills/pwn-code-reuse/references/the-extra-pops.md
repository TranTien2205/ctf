# The extra pops — the scratch registers


`pop rsi; pop r15` — the r15 is scratch: give it a benign value (0)
unless a later gadget reads it; a combined pop is a feature when both
registers are needed.
