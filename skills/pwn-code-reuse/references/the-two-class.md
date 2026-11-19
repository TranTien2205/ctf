# The two-class split — x86 vs x64 chains


The ABI difference is structural:

- x64: args in registers — pops set them; the chain is pop+arg pairs.
- x86: args on the stack — the chain is [func][ret][args...].

A chain built for the wrong ABI fails silently — check the binary's
class first (`file ./chal` or pwn_triage).
