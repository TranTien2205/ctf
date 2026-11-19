# Direct parameter access — the %N$p / %N$n syntax — case catalogue

The $ syntax addresses an argument by index: %7$p reads the 7th arg, %7$s derefs it, %7$n writes to it. The whole primitive is index-addressed.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | %7$p prints the 7th arg | indexed read | positional syntax |
| 2 | %N$n writes to the Nth arg | indexed write | the write |
| 3 | non-positional %p scans in order | incremental read | the scan |

## Falsifier

Falsifier — the format string can't address your argument's position: the primitive can't reach it.
