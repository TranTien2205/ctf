# The scanf family — a different boundary


scanf %s is a stack-corruption read, not a format string: the format in
scanf is the PARSE spec, and %s reads without a bound — a different
class.

| Call | Real class |
|---|---|
| scanf("%s",buf) | unbounded read → stack-smash |
| scanf(buf,...) | buf is the format — unusual but possible |

## The distinction

scanf %s is a READ primitive; printf %n is a WRITE. The class boundary
splits at the mechanism.

## Falsifier

The input goes to scanf %s not printf: the class is stack-overflow, not
format-string.
