# Question shape -> field -> command

Baseline first, always: `wc -l`, `head -1`, `tail -1` — volume + timeframe.

| Question | Field | Command |
|---|---|---|
| which IP | $1 (common formats) | `awk '{print $1}' log \| sort \| uniq -c \| sort -rn \| head` |
| which path | $7 in combined log | `awk -F'"' '{print $2}' log \| awk '{print $2}' \| sort \| uniq -c \| sort -rn \| head` |
| which status | $9 | `awk '{print $9}' log \| sort \| uniq -c \| sort -rn` |
| which user-agent | last quoted field | `awk -F'"' '{print $6}' log \| sort \| uniq -c \| sort -rn \| head` |
| failed logins | auth.log patterns | `grep -i 'failed\|invalid' auth.log \| awk '{print $9,$11}' \| sort \| uniq -c \| sort -rn` |
| what was downloaded | GET path + bytes | `grep -i 'flag\|download\|\.zip\|\.txt' access.log` |
| when X happened | timestamp field | `grep -n 'needle' log` then `sed -n 'N-10,N+10p' log` for context |
| command run | shell history in syslog | `grep -E 'COMMAND|cmd' syslog` |

## Reading the answer

- A count outlier at the top of `uniq -c` is the anomaly the question wants —
  1 request among 4000 is more interesting than the 3900-request crawler.
- The line AROUND the hit usually carries the real answer: the referer, the
  request right before it, the session it belongs to.
- Rotated siblings: `*.log.1`, `*.log.gz` — `zgrep`/`zcat` covers the earlier
  window; a one-file baseline can hide the whole anomaly.

## Traps

- IIS/nginx/apache field positions differ — print one full line and count
  fields before hard-coding `$7`.
- Timestamps may be UTC while the question expects local — state the zone
  the log uses.
