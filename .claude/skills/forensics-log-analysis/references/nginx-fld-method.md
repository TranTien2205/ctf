# HTTP method in a nginx access

**Log:** nginx access — `combined + request_time/upstream fields`.

**Field:** HTTP method — odd verbs.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
