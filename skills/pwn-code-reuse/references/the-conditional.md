# Conditional gadgets — the jump-in-the-middle


A gadget containing a conditional jump (test/jne) may not reach the
ret — the condition must hold; if it can't, the gadget is useless.

## The audit

pd the full tail — a gadget with a branch is only usable if the
branch condition is satisfiable or always false.
