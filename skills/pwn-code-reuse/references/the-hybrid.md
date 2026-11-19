# The hybrid — chain + planted code


When a small RWX region exists: a short chain writes/locates the
shellcode, jumps to it — hybrid ROP+shellcode.

## The shape

    [write/mprotect chain] [jmp the planted code]

## Falsifier

No executable region can be made: pure chain.
