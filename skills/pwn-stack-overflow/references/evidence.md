# Evidence — what proves each stage

| Stage | Evidence |
|---|---|
| Sink exists | the read call + the insufficient bound (file:line or disasm) |
| Offset measured | the faulting register's 4 pattern bytes + `--find` offset |
| Control proven | RIP holds your marker — the crash dump |
| Canary leaked | the leaked word's value at its stack offset |
| Chain lands | the function/syscall executes (output, or the flag) |
| Flag | bytes read from the live response |

## Commands

```bash
python3 tools/hooks.py post-probe <challenge> --verdict confirms \
  --hypothesis-id <id> --class pwn-stack-overflow \
  --evidence-kind class \
  --evidence 'RIP=0x6161616c at pattern offset 72' \
  --response '<the crash output/bytes it was read from>'
```

```bash
python3 tools/hooks.py pre-flag <challenge> \
  --value 'flag{...}' \
  --evidence '<the response/artifact bytes it was read from>'
```

## What does NOT count

- A crash without control — a segfault alone proves nothing.
- The offset from a textbook assumption — it must be measured.
- A flag-shaped string typed into the payload — only response bytes count.
- 'It should work' — only the observed execution counts.
