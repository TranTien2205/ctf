# HTTP method in a windows event log

**Log:** windows event log — `binary; convert with evtx_dump/EvtxECmd`.

**Field:** HTTP method — odd verbs.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
