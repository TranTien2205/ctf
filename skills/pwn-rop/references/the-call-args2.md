# More call args — the 4+ arg functions


rcx/r8/r9 set args 4-6 — the pops are scarcer; substitutes:

- A six-pop gadget (csu tail) sets rbx/rbp/r12-r15 — not the arg
  regs, but combined with movs.
- SROP sets everything.
- Pick a fewer-arg function (system over execve).
