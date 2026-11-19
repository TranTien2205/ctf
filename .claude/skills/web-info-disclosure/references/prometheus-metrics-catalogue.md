# Prometheus /metrics mining — case catalogue

A /metrics endpoint is a topology map: service names, queue names, error counts, request rates — and occasionally a flag-leaking label.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /metrics with # HELP/# TYPE lines | prometheus | read all metric names |
| 2 | custom app metrics | internal names | service map |
| 3 | label values with secrets/paths | leaking labels | read directly |

## Falsifier

Falsifier — no /metrics or it's stripped to standard runtime counters only: nothing extra disclosed.
