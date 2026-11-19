# The arg check — what the call actually receives


Before firing: verify the call's args — a register that "should" hold
the arg often holds something else (the gadget's side effect, a stale
value).

## The check

r2 -d at the call site: dr rdi rsi rdx — the actual argument values —
against the intended ones.
