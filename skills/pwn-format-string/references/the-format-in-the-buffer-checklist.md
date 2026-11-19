# The format-in-the-buffer — the primitive is that buf IS the format — checklist

Companion to `the-format-in-the-buffer.md`.

## Checklist

- [ ] Call | Format position | Notes
- [ ] printf(buf) | buf IS format | open
- [ ] snprintf(d,n,buf) | bounded output, same interpreter | open
- [ ] fprintf(f,buf) | to a stream | open
- [ ] 1. Confirm: your input reaches the format position.
- [ ] 2. The specifiers you write ARE the program — %p reads, %n writes.
- [ ] 3. The bounded-output case (snprintf) still runs the write.
