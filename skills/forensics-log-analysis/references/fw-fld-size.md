# response size in a firewall log

**Log:** firewall log — `allow/deny entries by rule`.

**Field:** response size — the data volume.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
