# Frame analysis — reading the exact layout from disassembly — checklist

The decisive pre-flight: disassemble the vulnerable function, map the locals/canary/saved-regs positions from the actual code — not the textbook model.

## Checklist

- [ ] r2 -A && pdf @ <vuln> — the prologue shows frame size, the canary load, the saved regs.
- [ ] The epilogue (leave;ret or pop rbp; ret) shows where the saved state sits.
- [ ] Map: input buffer offset → canary → saved RBP → saved RIP.
- [ ] The cyclic measurement then confirms the layout empirically.

## Abort conditions

- -fomit-frame-pointer removes the saved RBP — the layout shifts by 8.
- Compiler reorders locals — the buffer may sit AFTER other locals, closer to the canary.
- The cyclic-measured offset is the ground truth; the disasm explains it.

## Falsifier

Falsifier — the disassembly shows a fully-bounded read: the model says no overflow; trust the code, not the hope.
