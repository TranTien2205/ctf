# The format-literal boundary — when the class is closed — checklist

printf("%s", buf) passes your input as an ARGUMENT to a literal format — nothing is interpreted. The class is open only when your input IS the format argument.

## Checklist

- [ ] Find the call: is your input the format argument (1st arg to printf/fprintf) or an argument TO a literal format?
- [ ] printf(buf) → open; printf("%s",buf) → closed.
- [ ] snprintf(dst,n,buf) → buf is the format → open.
- [ ] A wrapper that always formats your input as %s → closed.

## Abort conditions

- The class is about WHO is the format string, not whether a string reaches printf.
- printf(input) is the bug; printf("%s",input) is safe.
- A wrapper like log(buf) that calls printf(buf) internally is still open.

## Falsifier

Falsifier — every call passes your input as an argument to a literal format: nothing is interpreted; the class is closed.
