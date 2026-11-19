# Misc specifiers — %a %e %g edge cases


Float specifiers (%a %e %g) read args as doubles — another leak form
that can show register bits %p wouldn't; %% is the literal.

## Use

- Float specifiers interpret the arg as a double — leaks bit patterns as
  floats.
- Mostly equivalent to %p for leaking; useful if %p output is filtered.
- %% is the only 'free' specifier — no arg.

## Falsifier

None; alternative read forms.
