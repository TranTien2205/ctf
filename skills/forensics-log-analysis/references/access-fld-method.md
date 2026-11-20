# HTTP method in a web access log

**Log:** web access log — `IP - - [time] "METHOD path HTTP/ver" status size "ref" "UA"`.

**Field:** HTTP method — odd verbs.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
