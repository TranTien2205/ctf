# The arg consumption — how specifiers walk the args


Each non-positional specifier consumes ONE argument position in order:
%p.%p.%p reads args 1,2,3. Positional %N$... addresses by index without
consuming.

## The rule

- %p.%p.%p → args 1,2,3.
- %7$p → arg 7, doesn't consume.
- A mix: glibc requires all-or-none positional in one call.

## The trap

A long %p run before the %n walks past your planted pointer — positional
args avoid the consumption.
