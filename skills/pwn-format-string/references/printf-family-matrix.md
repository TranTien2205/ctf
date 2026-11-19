# The printf-family matrix — which call is which

| Call | Format position | Notes |
|---|---|---|
| `printf(buf)` | buf IS format | open |
| `fprintf(f,buf)` | buf IS format | open |
| `sprintf(d,buf)` | buf IS format | open |
| `snprintf(d,n,buf)` | buf IS format | open |
| `printf("%s",buf)` | buf is an arg | CLOSED |
| `printf("%d",x)` | literal format | CLOSED |
| `log(buf)` calling `printf(buf)` | buf IS format | open |

A function that passes buf to printf internally is open even if the call
site looks safe.
