# Detection — naming it format-string — checklist

Signals the class is open: a printf-family call whose format argument is user-controlled, and the %p leak confirms it in one probe.

## Checklist

- [ ] Find the call site: is your input the format argument?
- [ ] Send 'AAAA.%p.%p.%p' — reflected pointers confirm the primitive.
- [ ] Locate your buffer's N with AAAA.%N$p.
- [ ] Choose read or write based on what the chain needs.

## Abort conditions

- The %p leak is the cheapest confirm in pwn — one probe.
- The class boundary is WHO is the format string, not whether a string reaches printf.

## Falsifier

Falsifier — the format argument is a literal (printf("%s",buf)): nothing is interpreted; the class is closed.
