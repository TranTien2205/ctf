# response size in a mail log

**Log:** mail log — `postfix/sendmail queue entries`.

**Field:** response size — the data volume.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
