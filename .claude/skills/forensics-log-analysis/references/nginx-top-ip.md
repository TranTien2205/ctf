# the top talker in a nginx access

**Log:** nginx access — `combined + request_time/upstream fields`.

**Question:** the top talker — which IP hammered the log.

Bracket with `log_summary.py summary`, then distribute the relevant field, then window the hit. Quote the verbatim line.
