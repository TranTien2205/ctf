# request path in a authentication log

**Log:** authentication log — `Mon DD HH:MM:SS host sshd[pid]: Accepted/Failed ... for USER from IP`.

**Field:** request path — what was asked for.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
