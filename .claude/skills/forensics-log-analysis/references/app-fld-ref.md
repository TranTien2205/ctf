# referer in a application log

**Log:** application log — `no standard layout — read head first`.

**Field:** referer — where it came from.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
