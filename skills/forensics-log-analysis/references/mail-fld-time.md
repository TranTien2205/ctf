# timestamp in a mail log

**Log:** mail log — `postfix/sendmail queue entries`.

**Field:** timestamp — the burst + timezone.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
