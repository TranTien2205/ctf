# The class boundary — reuse vs its neighbors


- vs pwn-stack-overflow: the overflow gives IP control; this class is
  what runs after — the boundary is the confirmed control.
- vs pwn-format-string: the %n write can land a chain's delivery or
  BE the redirect — the boundary is whether a ret-chain runs.
- vs pwn-heap-corruption: the heap write can plant the chain's bytes —
  the boundary is where the planted payload executes.

The class names the borrowed-code execution, not the corruption that
enabled it.
