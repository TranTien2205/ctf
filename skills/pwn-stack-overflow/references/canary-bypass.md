# Stack canary — leak it or write around it

A stack canary is a random word placed before the saved frame; smashing past it trips __stack_chk_fail. The bypass is always the same shape: get the canary's value, keep it intact in your payload.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| canary in protections | need its value | leak via format-string or info-leak |
| a read leaks stack content | canary recoverable | read and reuse |
| write past the canary crashes | smashing detected | route around the word |

## Steps

1. Confirm the canary from the %fs:0x28 load in disasm — not from the import list (static binaries lie).
2. Leak it: a format-string %p at the right depth, or an info-leak read that walks past the buffer.
3. Preserve it in the payload: put the leaked value at its exact offset; corrupt everything AFTER it freely.
4. If no leak exists, a forking server reuses the canary — brute it byte-by-byte through the crash behavior.

## Falsifier

Falsifier — no leak primitive exists and the canary blocks every write path: the class's stack route is closed; other classes (format-string, heap) may remain.

## Traps

- A forking server (per-connection fork) reuses ONE canary — byte-at-a-time brute is feasible (~256 × 8 checks).
- The canary sits between locals and saved regs — your write must land past it intact.
- A leaked canary is valid only for that process/fork — re-leak per connection if the server doesn't fork.

## Commands

```bash
r2 -A ./chal && pdf @ main | grep fs:0x28
```

## Cross-references

`protection-modes.md` · `format-string-leak.md` · `pie-leak.md`
