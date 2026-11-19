# The dead write — aiming at memory nobody reads


A write that lands but whose target is never consumed: the classic
failure of a "working" heap exploit — verify the firing condition.

## Check

- GOT/ret: fires on call/return — will the program reach it?
- Hook: fires on malloc/free — does one happen after?
- FILE: fires on stdio/exit — is exit reachable?
- App ptr: fires on its call — is the call reachable?

## Falsifier

No path from the write to the firing event: the slot is dead — aim at
one that fires.
