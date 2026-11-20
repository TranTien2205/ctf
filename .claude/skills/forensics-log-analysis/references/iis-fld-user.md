# username in a IIS W3C log

**Log:** IIS W3C log — `#Fields: directive names the columns`.

**Field:** username — who authenticated.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
