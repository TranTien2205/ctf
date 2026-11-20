# An AST/node check — the forgotten grammar

The checker rejects NODE TYPES, not strings — decorators, `with`,
exception args, f-strings may survive where a call node is refused.
A blacklisted word is still reachable via an object that carries it.

## The forgotten grammar

Decorators, with, exception args, lambda defaults, f-strings.
