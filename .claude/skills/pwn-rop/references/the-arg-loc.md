# The arg locations — where args live


Args live: in registers (pops), on the stack (x86/arg7+), in memory
(the pointer's target) — the chain supplies each where the callee
reads it.
