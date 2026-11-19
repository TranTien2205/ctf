# The complex call — multi-arg functions


Functions needing 4+ args (execve with env, mmap) need the rare
registers — the chain grows and the gadgets are scarcer.

## The substitutes

- ret2csu sets rdx/rsi/rdi at once.
- SROP sets everything.
- Choose a simpler function (system over execve) when a substitute
  can't be found.
