# The fmtstr in a later input — multi-field formats


The program may read several fields and printf ONE of them: the fmtstr
goes in that specific field, and earlier fields must pass their checks
first.

## Steps

1. Map the input protocol: which field reaches printf.
2. Fill earlier fields with valid values; put specifiers in the right
   one.
3. The field's position in the input stream doesn't change the
   arg-offset.

## Falsifier

The field never reaches a format position: re-map the input protocol.
