# referer in a mail log

**Log:** mail log — `postfix/sendmail queue entries`.

**Field:** referer — where it came from.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
