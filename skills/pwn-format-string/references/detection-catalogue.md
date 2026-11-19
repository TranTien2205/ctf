# Detection — naming it format-string — case catalogue

Signals the class is open: a printf-family call whose format argument is user-controlled, and the %p leak confirms it in one probe.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | printf(buf) with user input | the format is yours | open |
| 2 | a %p in input reflects a stack word | the leak confirms | the primitive |
| 3 | fprintf(f,buf) / snprintf(d,n,buf) | format position | open |
| 4 | printf("%s",buf) | arg position | closed |

## Falsifier

Falsifier — the format argument is a literal (printf("%s",buf)): nothing is interpreted; the class is closed.
