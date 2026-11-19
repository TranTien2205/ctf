# The format-literal boundary — when the class is closed

printf("%s", buf) passes your input as an ARGUMENT to a literal format — nothing is interpreted. The class is open only when your input IS the format argument.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| printf(buf) / fprintf(f,buf) | buf IS the format | open |
| printf("%s", buf) | buf is an arg | closed |
| snprintf(dst,n,buf) | buf IS the format | open |
| printf("%d",atoi(buf)) | buf is a converted arg | closed |

## Steps

1. Find the call: is your input the format argument (1st arg to printf/fprintf) or an argument TO a literal format?
2. printf(buf) → open; printf("%s",buf) → closed.
3. snprintf(dst,n,buf) → buf is the format → open.
4. A wrapper that always formats your input as %s → closed.

## Falsifier

Falsifier — every call passes your input as an argument to a literal format: nothing is interpreted; the class is closed.

## Traps

- The class is about WHO is the format string, not whether a string reaches printf.
- printf(input) is the bug; printf("%s",input) is safe.
- A wrapper like log(buf) that calls printf(buf) internally is still open.

## Commands

```bash
r2 -A ./chal && pdf @ <func> | grep -iE 'printf|format'
```

## Cross-references

`primitive-matrix.md`
