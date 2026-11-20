# the top talker in a web access log

**Log:** web access log — `IP - - [time] "METHOD path HTTP/ver" status size "ref" "UA"`.

**Question:** the top talker — which IP hammered the log.

Bracket with `log_summary.py summary`, then distribute the relevant field, then window the hit. Quote the verbatim line.
