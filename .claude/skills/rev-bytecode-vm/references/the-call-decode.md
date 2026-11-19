# Call/ret decoding — the subroutines

A VM with call/ret has subroutines — the check may be a called
function, not the main stream.

## The handlers

    case 0x40: stack_ret.push(pc); pc = prog[pc];   // call addr
    case 0x41: pc = stack_ret.pop();                // ret

## The decode

Follow calls into their target blocks — a `check` subroutine at a
fixed offset is the verifier; decode it like the main stream.

## The recursion note

A recursive VM program (call into itself) — decode each call target
once; mark visited blocks.
