# The redirect's argument — what your target receives


A redirect fires with whatever args the CALL SITE set: GOT[puts]→system
only gives a shell if puts was called with a controllable string.

## Steps

1. Identify which import is called next AND what its arg is.
2. If the arg is your input: redirect → system gives system(your_input).
3. If the arg is fixed: the redirect calls your target with the wrong
   arg — useless or partial.
4. Pick the import whose call-site arg is most controllable.

## Falsifier

No import is called after the write with a useful arg state: GOT
redirects are inert.
