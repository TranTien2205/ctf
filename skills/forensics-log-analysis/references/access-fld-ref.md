# referer in a web access log

**Log:** web access log — `IP - - [time] "METHOD path HTTP/ver" status size "ref" "UA"`.

**Field:** referer — where it came from.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
