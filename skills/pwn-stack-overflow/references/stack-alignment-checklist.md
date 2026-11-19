# Stack alignment — the movaps crash — checklist

x64 libc functions (especially system, printf) use movaps on the stack, which faults on misaligned RSP. A chain that crashes on the call site needs an extra 'ret' gadget for alignment.

## Checklist

- [ ] If the libc call crashes with a segv at a movaps on the stack, RSP is misaligned.
- [ ] Insert a 'ret' gadget (no-op) before the call to bump RSP by 8.
- [ ] Test both parities — the needed alignment depends on where the chain entered.

## Abort conditions

- The classic symptom: 'works locally, crashes remotely' — a 16-byte alignment shift.
- An even vs odd number of returns before the call is what matters.

## Falsifier

Falsifier — the crash isn't alignment (it's a real arg/register problem): the ret-pad doesn't fix it; re-debug the chain.
