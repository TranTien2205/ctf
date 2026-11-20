# Deep: Window/buffering tells

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`tcp.window_size_value` collapsed to 0 = receiver stalled; zero-window during a transfer caps the measured rate (a slow upload may be receiver-throttled, not attacker-paced). Rarely load-bearing in CTF but explains a 'suspiciously slow' transfer.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.
