# sprintf — the formatted write gadget


sprintf(dst, fmt, ...) writes formatted output to dst — a chain-
callable writer that composes strings (or worse, a format-string bug
if fmt is controlled).

## The danger

An attacker-controlled fmt IS a format-string bug — verify fmt is
fixed before using it as a plant path.
