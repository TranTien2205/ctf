# Negative shapes - what a dead race looks like

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

- serial baseline already produces the outcome: the endpoint
  simply accepts repeats - that is a replay/logic question, not a
  race; recorded as 'no concurrency needed'.
- overlap proven but outcome count equals the serial rate: the
  window exists but does not decide anything; recorded as
  'overlapped, no differential'.
- the requests never overlapped: the tool's own measurement says
  so; the run does not count as a probe of the window at all.
- the second request is refused on a lock/idempotency key: the
  app defends correctly; the record names which defence fired.

## Ledger lines

Each shape writes ONE negative line with its measurement - 'N
overlapped attempts, K=baseline' is the falsifier evidence, not a
guess that the mechanism is absent.

## Pivot

All shapes negative -> the class closes for this endpoint; the next
endpoint or the next class per decide.py.
