# Direct parameter access — the %N$p / %N$n syntax — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| %7$p prints the 7th arg | indexed read | positional syntax |
| %N$n writes to the Nth arg | indexed write | the write |
| non-positional %p scans in order | incremental read | the scan |

## Falsifier

Falsifier — the format string can't address your argument's position: the primitive can't reach it.
