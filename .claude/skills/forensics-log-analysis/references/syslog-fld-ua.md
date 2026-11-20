# user-agent in a system log

**Log:** system log — `Mon DD HH:MM:SS host daemon[pid]: message`.

**Field:** user-agent — the tool signature.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
