# COP — call-oriented chains


Call gadgets (`call [rX]` / `call reg`) chain like JOP but via call —
the return address lands on the stack; ending the call-gadget sequence
needs a matching ret or a terminal call.

## Falsifier

Same as JOP — the fallback when ret-gadgets are missing.
