# ret-equivalents — the gadget endings


Gadgets can end other than `ret`:

- `pop rXX; <more>; jmp ...` — if the jmp targets controlled code.
- `leave; ret` — the pivot ending.
- `call rXX` where the called function returns to your next qword.

## The rule

The ending must transfer to a stack-pulled or controlled target —
the audit checks the tail's last instruction.
