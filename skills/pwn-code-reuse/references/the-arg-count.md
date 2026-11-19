# How many args — the chain's size driver


The call's arg count drives the chain length:

- 1 arg (system): pop rdi + call.
- 2 args: + pop rsi.
- 3 args (execve/read/mprotect): + pop rdx.
- More: the rare registers.

Minimize the arg count: prefer system over execve, a 1-arg function
over a 3-arg one.
