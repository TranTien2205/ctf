# response size in a structured JSON log

**Log:** structured JSON log — `one object per line, named fields`.

**Field:** response size — the data volume.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
