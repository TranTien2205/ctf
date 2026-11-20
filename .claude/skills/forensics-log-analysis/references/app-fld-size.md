# response size in a application log

**Log:** application log — `no standard layout — read head first`.

**Field:** response size — the data volume.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
