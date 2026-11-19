# Writing near environ — stack-reach via libc


environ's VALUE points at the stack — and environ itself is a libc
global you can write: overwrite environ to redirect getenv-style reads,
or leak it for the stack.

## Steps

1. libc base → environ_addr = base + offset.
2. Read environ → a stack address (leak).
3. Or write environ → later env reads see your pointer's data.

## Falsifier

No primitive reaches libc's .data: environ is out of reach.
