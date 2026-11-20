# referer in a DNS query log

**Log:** DNS query log — `queries by source IP`.

**Field:** referer — where it came from.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
