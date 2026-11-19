# Frame analysis — reading the exact layout from disassembly

The decisive pre-flight: disassemble the vulnerable function, map the locals/canary/saved-regs positions from the actual code — not the textbook model.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| prologue: sub rsp, N | frame size | locals start at rsp |
| canary load: mov rax, fs:0x28 | canary present | position at rsp+N-8 or so |
| leave/ret or pop rbp; ret | epilogue shape | saved regs position |

## Steps

1. r2 -A && pdf @ <vuln> — the prologue shows frame size, the canary load, the saved regs.
2. The epilogue (leave;ret or pop rbp; ret) shows where the saved state sits.
3. Map: input buffer offset → canary → saved RBP → saved RIP.
4. The cyclic measurement then confirms the layout empirically.

## Falsifier

Falsifier — the disassembly shows a fully-bounded read: the model says no overflow; trust the code, not the hope.

## Traps

- -fomit-frame-pointer removes the saved RBP — the layout shifts by 8.
- Compiler reorders locals — the buffer may sit AFTER other locals, closer to the canary.
- The cyclic-measured offset is the ground truth; the disasm explains it.

## Commands

```bash
r2 -A ./chal && pdf @ <vuln>
r2 -A ./chal && afi @ <vuln>
```

## Cross-references

`saved-regs.md` · `offset-measurement.md`
