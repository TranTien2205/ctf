# Detection — naming it format-string

Signals the class is open: a printf-family call whose format argument is user-controlled, and the %p leak confirms it in one probe.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| printf(buf) with user input | the format is yours | open |
| a %p in input reflects a stack word | the leak confirms | the primitive |
| fprintf(f,buf) / snprintf(d,n,buf) | format position | open |
| printf("%s",buf) | arg position | closed |

## Steps

1. Find the call site: is your input the format argument?
2. Send 'AAAA.%p.%p.%p' — reflected pointers confirm the primitive.
3. Locate your buffer's N with AAAA.%N$p.
4. Choose read or write based on what the chain needs.

## Falsifier

Falsifier — the format argument is a literal (printf("%s",buf)): nothing is interpreted; the class is closed.

## Traps

- The %p leak is the cheapest confirm in pwn — one probe.
- The class boundary is WHO is the format string, not whether a string reaches printf.

## Cross-references

`format-literal-boundary.md` · `primitive-matrix.md`
