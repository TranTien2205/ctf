# The arg consumption — how specifiers walk the args — checklist

Companion to `the-arg-consumption.md`.

## Checklist

- [ ] %p.%p.%p → args 1,2,3.
- [ ] %7$p → arg 7, doesn't consume.
- [ ] A mix: glibc requires all-or-none positional in one call.
