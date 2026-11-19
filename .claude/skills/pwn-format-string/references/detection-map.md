# Detection — naming it format-string — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| printf(buf) with user input | the format is yours | open |
| a %p in input reflects a stack word | the leak confirms | the primitive |
| fprintf(f,buf) / snprintf(d,n,buf) | format position | open |
| printf("%s",buf) | arg position | closed |

## Falsifier

Falsifier — the format argument is a literal (printf("%s",buf)): nothing is interpreted; the class is closed.
