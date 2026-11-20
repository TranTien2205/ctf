# service/daemon in a firewall log

**Log:** firewall log — `allow/deny entries by rule`.

**Field:** service/daemon — which service logged.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
