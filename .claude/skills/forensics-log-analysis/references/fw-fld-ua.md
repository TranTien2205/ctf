# user-agent in a firewall log

**Log:** firewall log — `allow/deny entries by rule`.

**Field:** user-agent — the tool signature.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
