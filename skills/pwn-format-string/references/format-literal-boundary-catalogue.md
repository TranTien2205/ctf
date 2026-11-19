# The format-literal boundary — when the class is closed — case catalogue

printf("%s", buf) passes your input as an ARGUMENT to a literal format — nothing is interpreted. The class is open only when your input IS the format argument.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | printf(buf) / fprintf(f,buf) | buf IS the format | open |
| 2 | printf("%s", buf) | buf is an arg | closed |
| 3 | snprintf(dst,n,buf) | buf IS the format | open |
| 4 | printf("%d",atoi(buf)) | buf is a converted arg | closed |

## Falsifier

Falsifier — every call passes your input as an argument to a literal format: nothing is interpreted; the class is closed.
