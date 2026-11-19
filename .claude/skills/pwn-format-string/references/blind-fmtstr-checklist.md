# Blind format string — no reflected output — checklist

Sometimes the printf output isn't returned to you: the primitive exists but you can't see the leak. Blind techniques read via a side channel or write blindly.

## Checklist

- [ ] If the output isn't reflected: %s at a controlled address either crashes (bad addr) or doesn't — a 1-bit oracle.
- [ ] A blind %n write can still redirect control — the effect shows in behavior.
- [ ] Some services echo via a second channel (stderr, a log, a follow-up read).
- [ ] A blind fmtstr is weaker — prefer finding the output path first.

## Abort conditions

- A %s at an unmapped address crashes — a 1-bit read oracle.
- Blind writes don't confirm — verify via the behavior change.
- Look for the echo in a second response/channel before concluding blind.

## Falsifier

Falsifier — no output channel and no usable side-channel oracle: the read primitive can't be harvested; only a blind write remains.
