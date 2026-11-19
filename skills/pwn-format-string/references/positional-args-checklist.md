# Direct parameter access — the %N$p / %N$n syntax — checklist

The $ syntax addresses an argument by index: %7$p reads the 7th arg, %7$s derefs it, %7$n writes to it. The whole primitive is index-addressed.

## Checklist

- [ ] %N$p reads argument N; %N$s derefs it; %N$n writes to it.
- [ ] Find N where your planted pointer/data sits — the arg-offset-finder.
- [ ] x64: args 1-6 in registers; the stack args are N≥6 or 7.
- [ ] Non-positional %p.%p.%p scans args in order — the incremental read.

## Abort conditions

- glibc requires all specifiers in one call to be positional if any is — mixing fails.
- The offset N shifts with the call's frame depth.
- Argument 1 is the format string itself in some ABIs — check the indexing.

## Falsifier

Falsifier — the format string can't address your argument's position: the primitive can't reach it.
