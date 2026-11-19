# Frame analysis — reading the exact layout from disassembly — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| prologue: sub rsp, N | frame size | locals start at rsp |
| canary load: mov rax, fs:0x28 | canary present | position at rsp+N-8 or so |
| leave/ret or pop rbp; ret | epilogue shape | saved regs position |

## Falsifier

Falsifier — the disassembly shows a fully-bounded read: the model says no overflow; trust the code, not the hope.
