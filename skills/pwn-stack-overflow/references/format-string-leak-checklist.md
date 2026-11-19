# Format string as a leak primitive — checklist

A format-string read (%p, %s, %x) dumps stack/registers — the leak primitive that feeds canary and PLE leaks. Ownership is pwn-format-string's class; this file is the bridge.

## Checklist

- [ ] Confirm the format-string vulnerability (pwn-format-string class).
- [ ] Use %p at increasing depths until the leaked word matches a code/data/canary shape.
- [ ] Read the canary's offset on the stack for canary-bypass, or a code pointer for PIE-leak.
- [ ] Feed the leak into the stack-overflow chain.

## Abort conditions

- The leak is pwn-format-string's mechanism — this file only explains the chain.
- Different stack depths each call — the offset to the canary varies; measure once, use it.

## Falsifier

Falsifier — the format-string isn't controllable to the needed depth, or the target value isn't on the stack: no leak via this path.
