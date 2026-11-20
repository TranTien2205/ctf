# status code in a firewall log

**Log:** firewall log — `allow/deny entries by rule`.

**Field:** status code — the anomaly surface.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
