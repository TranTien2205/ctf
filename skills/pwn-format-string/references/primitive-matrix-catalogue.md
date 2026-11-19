# The format-specifier matrix — what each one buys — case catalogue

The specifier is the whole primitive: %p/%x read, %s dereferences, %n/%hn/%hhn write. Choosing the right one IS the exploit.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | %p/%x in a leaked output | read primitive | the leak |
| 2 | %s at a planted pointer | arbitrary read | the deref |
| 3 | %n/%hn/%hhn | arbitrary write | the write |
| 4 | a literal %s or %p | interprets nothing | closed |

## Falsifier

Falsifier — the format argument is a literal and your input is an argument to it (printf("%s", buf)): nothing is interpreted; the class is closed.
