# username in a application log

**Log:** application log — `no standard layout — read head first`.

**Field:** username — who authenticated.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
