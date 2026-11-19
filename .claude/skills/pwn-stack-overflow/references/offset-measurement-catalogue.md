# Offset measurement — getting the exact byte count — case catalogue

The offset IS the bug's geometry: input_start → saved_return_address. Measure it empirically; never guess.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | input length varies the crash point | offset measurable | cyclic method |
| 2 | a fixed-size crash regardless of input | bound is fixed | bound-limited — check |

## Falsifier

Falsifier — no input length produces a faulting RIP holding pattern bytes: the write doesn't reach saved state at this length; re-check the bound.
