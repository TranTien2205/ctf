# Worked — a math-rounds service

1. net_dialog -> banner `round N: a+b=?` + `> ` terminator.
2. Solver: until(b'> ') -> regex the ints -> send sum + \n.
3. Round 40 adds `*` — the lenient parse survives; the log shows the drift.
4. Flag on round 100 — transcript is the proof.

## The chain

net_dialog -> until -> regex -> sum -> flag on round 100.

## The chain

net_dialog -> until -> regex -> sum -> flag on round 100.
