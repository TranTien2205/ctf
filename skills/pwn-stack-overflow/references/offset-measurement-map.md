# Offset measurement — getting the exact byte count — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| input length varies the crash point | offset measurable | cyclic method |
| a fixed-size crash regardless of input | bound is fixed | bound-limited — check |

## Falsifier

Falsifier — no input length produces a faulting RIP holding pattern bytes: the write doesn't reach saved state at this length; re-check the bound.
