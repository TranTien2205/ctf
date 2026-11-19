# The printf-family matrix — which call is which — map

Companion to `printf-family-matrix.md`.

| Call | Format position | Notes |
|---|---|---|
| `printf(buf)` | buf IS format | open |
| `fprintf(f,buf)` | buf IS format | open |
| `sprintf(d,buf)` | buf IS format | open |
| `snprintf(d,n,buf)` | buf IS format | open |
| `printf("%s",buf)` | buf is an arg | CLOSED |
| `printf("%d",x)` | literal format | CLOSED |
| `log(buf)` calling `printf(buf)` | buf IS format | open |
