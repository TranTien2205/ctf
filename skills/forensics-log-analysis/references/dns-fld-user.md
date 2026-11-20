# username in a DNS query log

**Log:** DNS query log — `queries by source IP`.

**Field:** username — who authenticated.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
