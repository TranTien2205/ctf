# NX forces reuse — why the payload is borrowed


With NX on, no writable page executes: shellcode can't run, so the
payload borrows the binary's own instructions — gadget tails ending in
ret/call/jmp.

## The consequence

- Every action is a gadget: pop a register, a syscall, a call.
- The chain is a stack of gadget addresses + arguments.
- Missing gadgets constrain what the chain can express.

## Falsifier

NX is off: inject shellcode instead — the reuse machinery is needless.
