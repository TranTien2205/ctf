# The one-shot — no re-entry


No re-entry means: the leak and the real chain must coexist in one
run — or no leak at all.

## The shapes

- Leak-free: static binary syscall chain, non-PIE ret2plt ending
  at an imported system.
- One-run leak+chain: the chain itself prints the leak AND does the
  work — needs the leak's value in the SAME run (a call reading the
  just-printed value — rare; usually needs a two-call pattern where
  the leaked base feeds a computed call within the run).
