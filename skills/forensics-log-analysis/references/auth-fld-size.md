# response size in a authentication log

**Log:** authentication log — `Mon DD HH:MM:SS host sshd[pid]: Accepted/Failed ... for USER from IP`.

**Field:** response size — the data volume.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
