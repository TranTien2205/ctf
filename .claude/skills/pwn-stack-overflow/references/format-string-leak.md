# Format string as a leak primitive

A format-string read (%p, %s, %x) dumps stack/registers — the leak primitive that feeds canary and PLE leaks. Ownership is pwn-format-string's class; this file is the bridge.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| printf(user_input) or similar | format leak exists | %p leak |
| a %p that shows stack words | canary/pointer leak | read the right depth |

## Steps

1. Confirm the format-string vulnerability (pwn-format-string class).
2. Use %p at increasing depths until the leaked word matches a code/data/canary shape.
3. Read the canary's offset on the stack for canary-bypass, or a code pointer for PIE-leak.
4. Feed the leak into the stack-overflow chain.

## Falsifier

Falsifier — the format-string isn't controllable to the needed depth, or the target value isn't on the stack: no leak via this path.

## Traps

- The leak is pwn-format-string's mechanism — this file only explains the chain.
- Different stack depths each call — the offset to the canary varies; measure once, use it.

## Commands

```bash
r2 -A ./chal && pdf @ <func_with_printf>
```

## Cross-references

`../pwn-format-string/` · `canary-bypass.md` · `pie-leak.md`
