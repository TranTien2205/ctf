# timestamp in a DNS query log

**Log:** DNS query log — `queries by source IP`.

**Field:** timestamp — the burst + timezone.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
