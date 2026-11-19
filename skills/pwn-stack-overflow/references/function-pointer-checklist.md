# Function-pointer overwrite — the indirect-call target — checklist

A function pointer stored on the stack (a callback, a handler table, an atexit entry) that's overwritten becomes a controlled call site — call instead of return.

## Checklist

- [ ] Find a function pointer the code calls AFTER your write point.
- [ ] Overwrite the pointer with the target address.
- [ ] The next indirect call goes to your target — system() if the arg registers are right.
- [ ] The arg to the call is whatever the calling code set — check what it passes.

## Abort conditions

- The call's arguments come from the call site, not your payload — check what rdi holds.
- A vtable pointer overwrite is the C++ version of this.
- atexit hooks run on clean exit — a clean exit path can trigger your call.

## Falsifier

Falsifier — no function pointer reachable by the write, or none is called after the write point: no call-control.
