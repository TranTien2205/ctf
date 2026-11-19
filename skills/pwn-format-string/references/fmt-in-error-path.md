# Fmtstr in error paths — the handler case


The format call may sit in an error/log path that only fires on invalid
input: trigger the path first (send bad data), then the fmtstr payload in
the field that reaches it.

## Steps

1. Identify the error path's trigger condition.
2. Put the specifiers in the field that lands in the printf.
3. The error path's frame affects the arg-offset — measure there.

## Falsifier

The error path can't be triggered or the field doesn't reach the format
position.
