# _dl_runtime_resolve — the resolver itself


The lazy-binding resolver is itself a code path — attacking it (the
ret2dlresolve technique) forges a resolution that returns any function
without knowing libc.

## The shape (advanced)

1. Control the link_map / the resolution structures' index.
2. The resolver computes a symbol from a forged entry — returns the
   chosen function's address.
3. ret-into-resolver = arbitrary libc function call without a leak.

## Falsifier

Full RELRO (no lazy binding at all): the resolver path doesn't run —
the technique needs lazy binding.
