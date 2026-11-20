# referer in a structured JSON log

**Log:** structured JSON log — `one object per line, named fields`.

**Field:** referer — where it came from.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
