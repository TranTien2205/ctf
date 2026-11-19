# The format-specifier matrix — what each one buys — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| %p/%x in a leaked output | read primitive | the leak |
| %s at a planted pointer | arbitrary read | the deref |
| %n/%hn/%hhn | arbitrary write | the write |
| a literal %s or %p | interprets nothing | closed |

## Falsifier

Falsifier — the format argument is a literal and your input is an argument to it (printf("%s", buf)): nothing is interpreted; the class is closed.
