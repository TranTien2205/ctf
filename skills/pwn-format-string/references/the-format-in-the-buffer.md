# The format-in-the-buffer — the primitive is that buf IS the format


The vulnerability is a call whose format argument is your input:
printf(buf), snprintf(d,n,buf), fprintf(f,buf). The buffer itself is the
interpreter's program.

| Call | Format position | Notes |
|---|---|---|
| printf(buf) | buf IS format | open |
| snprintf(d,n,buf) | bounded output, same interpreter | open |
| fprintf(f,buf) | to a stream | open |

## Steps

1. Confirm: your input reaches the format position.
2. The specifiers you write ARE the program — %p reads, %n writes.
3. The bounded-output case (snprintf) still runs the write.

## Falsifier

The input is an argument to a literal format: nothing is interpreted.
