# The shellcode hybrid — chain to code


A chain that ends at executable shellcode: mprotect + write + jump —
or a found RWX page + write + jump.

## The recipe

    [chain: write shellcode to WX or mprotect it]
    [jmp/call the shellcode's address]

## Falsifier

No way to get executable memory: pure chain.
