# username in a apache access

**Log:** apache access — `common/combined format, $1 IP $7 path $9 status`.

**Field:** username — who authenticated.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
