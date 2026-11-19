# The scratch slots — r15 and friends


`pop rsi; pop r15; ret` sets rsi AND r15 — the r15 value is a scratch:
fill it with anything; it doesn't matter unless a later gadget uses
r15.

## The rule

Accept combined pops — the extra register is noise you tolerate.
Watch for a later gadget that reads the scratch: sequence matters.
