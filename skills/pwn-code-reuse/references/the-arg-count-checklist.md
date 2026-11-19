# How many args — the chain's size driver — checklist

Companion to `the-arg-count.md`.

## Checklist

- [ ] 1 arg (system): pop rdi + call.
- [ ] 2 args: + pop rsi.
- [ ] 3 args (execve/read/mprotect): + pop rdx.
- [ ] More: the rare registers.
