# request path in a mail log

**Log:** mail log — `postfix/sendmail queue entries`.

**Field:** request path — what was asked for.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
