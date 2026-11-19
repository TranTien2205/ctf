# Register preservation — which survive


Across a call, some registers are callee-saved (rbx, rbp, r12-r15) —
they survive the called function; caller-saved (rax, rdi...) are
clobbered.

## The rule

If a later gadget needs a value set EARLY, put it in a callee-saved
register — or set it after the call.
