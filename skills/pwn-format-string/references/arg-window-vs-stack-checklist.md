# The arg window vs raw stack — what %N$p actually sees — checklist

Companion to `arg-window-vs-stack.md`.

## Checklist

- [ ] 1. The declared varargs end at the call's arity — beyond that, %N$p reads
- [ ] 2. Your input buffer may BE a stack arg or stack memory at higher N.
- [ ] 3. Higher N reaches the caller's saved registers and return addresses.
