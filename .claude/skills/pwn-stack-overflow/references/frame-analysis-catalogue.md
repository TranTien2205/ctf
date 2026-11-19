# Frame analysis — reading the exact layout from disassembly — case catalogue

The decisive pre-flight: disassemble the vulnerable function, map the locals/canary/saved-regs positions from the actual code — not the textbook model.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | prologue: sub rsp, N | frame size | locals start at rsp |
| 2 | canary load: mov rax, fs:0x28 | canary present | position at rsp+N-8 or so |
| 3 | leave/ret or pop rbp; ret | epilogue shape | saved regs position |

## Falsifier

Falsifier — the disassembly shows a fully-bounded read: the model says no overflow; trust the code, not the hope.
