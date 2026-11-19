# The call site — what the fired call needs


Before redirecting to system/execve, check what the call site passes:
the arg register/operand at the redirect point decides whether your
target gets a useful argument.

## The check

- If the redirect fires through a function pointer, the caller sets
  the arg — usually your input buffer.
- If the redirect lands mid-function, the arg is whatever the register
  already holds.

## Falsifier

The call's argument can't be a useful string: the redirect's value is
limited — pick a target that needs no arg (a win function).
