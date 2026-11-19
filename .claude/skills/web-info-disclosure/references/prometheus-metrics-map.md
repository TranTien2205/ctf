# Prometheus /metrics mining — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /metrics with # HELP/# TYPE lines | prometheus | read all metric names |
| custom app metrics | internal names | service map |
| label values with secrets/paths | leaking labels | read directly |

## Falsifier

Falsifier — no /metrics or it's stripped to standard runtime counters only: nothing extra disclosed.
