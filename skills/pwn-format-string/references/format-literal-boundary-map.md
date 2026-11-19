# The format-literal boundary — when the class is closed — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| printf(buf) / fprintf(f,buf) | buf IS the format | open |
| printf("%s", buf) | buf is an arg | closed |
| snprintf(dst,n,buf) | buf IS the format | open |
| printf("%d",atoi(buf)) | buf is a converted arg | closed |

## Falsifier

Falsifier — every call passes your input as an argument to a literal format: nothing is interpreted; the class is closed.
