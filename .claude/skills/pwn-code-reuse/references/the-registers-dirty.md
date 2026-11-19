# Register state at the overwrite — the free args


At the overwrite point, registers already hold values — sometimes an
arg is already in place: check r2 -d at the overwrite to see what
rdi/rsi already carry.

## The free win

If rdi already points at your buffer: the call's arg is pre-set — skip
the pop.

## Falsifier

The needed register holds unusable data: pop it anyway.
