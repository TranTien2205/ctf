# The paired pop — two regs in one gadget


`pop rsi; pop r15; ret`-shaped gadgets set two registers — useful when
a single-register pop is missing; the r15 is a tolerated scratch.

## The rule

Give the scratch a benign value; check no later gadget reads it.
