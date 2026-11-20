# request path in a application log

**Log:** application log — `no standard layout — read head first`.

**Field:** request path — what was asked for.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
