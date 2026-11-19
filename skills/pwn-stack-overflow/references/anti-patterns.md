# Anti-patterns — moves that look right and waste budget

## Guessing the offset

Sending 'A'*k for different k and hoping. Fix: ONE cyclic send + --find.

## Building a chain before the protections report

Writing ROP without knowing if PIE/canary/RELRO are on. Fix: pwn_triage
first — the report decides the chain's shape.

## Treating a crash as control

'It segfaults' is not 'I control RIP'. Fix: check the faulting register
holds your pattern bytes.

## Assuming the textbook frame layout

locals→canary→saved-RBP→saved-RIP is the model, but optimization and
-fomit-frame-pointer shift it. Fix: measure offsets.

## Picking a shellcode stub with banned bytes

execve64 contains \x00 and the read is fgets: the payload dies at the
newline/null. Fix: match the stub to the read's allowed byte set.

## Ignoring stack alignment

'works locally, crashes remotely' is the movaps signature. Fix: a ret
gadget before the libc call.

## Re-trying the same chain after a falsifier fires

The canary tripped; changing padding length doesn't help. Fix: the
mechanism is wrong — leak the canary or route around it.

## Claiming the flag from the payload

A flag-shaped string you sent is not a flag. Fix: pre-flag on response
bytes only.
