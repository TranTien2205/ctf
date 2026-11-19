# The .bss write region — the plant area


.bss is writable and (non-PIE) fixed — the standard region for planted
strings and staged chains.

## The use

- Plant "/bin/sh" there via a write/read.
- Plant the stage-2 chain there; pivot into it.
- Plant fake structures (ret2dlresolve's tables).
