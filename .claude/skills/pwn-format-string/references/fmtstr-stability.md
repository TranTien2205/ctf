# Offset stability — does N survive across calls?


The arg-offset N is stable per CALL SITE, not per program: a loop reuses
the same site (stable); a different printf elsewhere may place your input
at a different N.

## Steps

1. Within one call site, N is constant.
2. Different call sites → different frames → possibly different N.
3. A recursive site → N shifts with depth.

## Falsifier

N differs at the site you actually use: re-measure at that site.
