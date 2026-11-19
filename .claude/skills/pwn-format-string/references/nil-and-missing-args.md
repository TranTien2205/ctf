# Nil and missing args — the read boundary


Reading past the provided arg count yields nil — %p on nil prints 'nil';
%s on nil errors. The window past your args tells you the call's true
arity.

## Steps

1. Scan %N$p upward — when values turn to (nil), you've passed the real
   args.
2. The real arg count bounds the useful N range.
3. Past-window reads error — treat as the scan's end.

## Falsifier

None; nil reads are informational. (nil) at arg N means fewer than N
varargs — stack args beyond the varargs still print real stack words.
