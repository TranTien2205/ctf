# a scanner burst in a web access log

**Log:** web access log — `IP - - [time] "METHOD path HTTP/ver" status size "ref" "UA"`.

**Question:** a scanner burst — 404 burst + tool UA.

Bracket with `log_summary.py summary`, then distribute the relevant field, then window the hit. Quote the verbatim line.
