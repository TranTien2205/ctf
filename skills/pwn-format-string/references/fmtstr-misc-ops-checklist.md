# Misc specifiers — %a %e %g edge cases — checklist

Companion to `fmtstr-misc-ops.md`.

## Checklist

- [ ] Float specifiers interpret the arg as a double — leaks bit patterns as
- [ ] Mostly equivalent to %p for leaking; useful if %p output is filtered.
- [ ] %% is the only 'free' specifier — no arg.
