# request path in a DNS query log

**Log:** DNS query log — `queries by source IP`.

**Field:** request path — what was asked for.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
