# HTTP method in a system log

**Log:** system log — `Mon DD HH:MM:SS host daemon[pid]: message`.

**Field:** HTTP method — odd verbs.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
