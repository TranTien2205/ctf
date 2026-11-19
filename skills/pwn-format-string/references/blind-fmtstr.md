# Blind format string — no reflected output

Sometimes the printf output isn't returned to you: the primitive exists but you can't see the leak. Blind techniques read via a side channel or write blindly.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| the format executes but output isn't shown | blind | side-channel read |
| a %s read can trigger a crash on bad addr | crash oracle | read via crash |
| a write still works blind | %n without feedback | the write |

## Steps

1. If the output isn't reflected: %s at a controlled address either crashes (bad addr) or doesn't — a 1-bit oracle.
2. A blind %n write can still redirect control — the effect shows in behavior.
3. Some services echo via a second channel (stderr, a log, a follow-up read).
4. A blind fmtstr is weaker — prefer finding the output path first.

## Falsifier

Falsifier — no output channel and no usable side-channel oracle: the read primitive can't be harvested; only a blind write remains.

## Traps

- A %s at an unmapped address crashes — a 1-bit read oracle.
- Blind writes don't confirm — verify via the behavior change.
- Look for the echo in a second response/channel before concluding blind.

## Cross-references

`leak-via-p.md`
