# Direct parameter access — the %N$p / %N$n syntax

The $ syntax addresses an argument by index: %7$p reads the 7th arg, %7$s derefs it, %7$n writes to it. The whole primitive is index-addressed.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| %7$p prints the 7th arg | indexed read | positional syntax |
| %N$n writes to the Nth arg | indexed write | the write |
| non-positional %p scans in order | incremental read | the scan |

## Steps

1. %N$p reads argument N; %N$s derefs it; %N$n writes to it.
2. Find N where your planted pointer/data sits — the arg-offset-finder.
3. x64: args 1-6 in registers; the stack args are N≥6 or 7.
4. Non-positional %p.%p.%p scans args in order — the incremental read.

## Falsifier

Falsifier — the format string can't address your argument's position: the primitive can't reach it.

## Traps

- glibc requires all specifiers in one call to be positional if any is — mixing fails.
- The offset N shifts with the call's frame depth.
- Argument 1 is the format string itself in some ABIs — check the indexing.

## Cross-references

`arg-offset-finder.md` · `the-stack-args.md`
