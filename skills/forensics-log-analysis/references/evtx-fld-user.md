# username in a windows event log

**Log:** windows event log — `binary; convert with evtx_dump/EvtxECmd`.

**Field:** username — who authenticated.

Get the column right for this format, then `cut|sort|uniq -c|sort -rn` — the outlier is the answer.
