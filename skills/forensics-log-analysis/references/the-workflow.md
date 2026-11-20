# The log-analysis workflow — bracket, distribute, find

A log file is the handout and the question is a fact inside it:
an IP, a user, a request, the moment something happened.
Extraction-shaped — find the line, quote it.

## The order

1. wc -l + head/tail — volume and timeframe; every later count
   claim needs the denominator.
2. Distribution first: cut the field of interest into
   sort|uniq -c|sort -rn — the anomaly is a count outlier.
3. grep the specific terms after the distribution shows normal.
4. Reconstruct the sequence: grep -n the hit, read ±20 lines.

## The local tool

    python3 tools/log_summary.py summary access.log
    python3 tools/log_summary.py field access.log --regex 'REGEX'
    python3 tools/log_summary.py window access.log --around N

summary gives line count, first/last lines, timestamp range,
per-hour histogram, top-N of IPs/users/paths/status codes plus
flag-like lines.

## The principle

The anomaly is almost always a count outlier or a shape that
doesn't fit the baseline — never the line you happened to grep.
Distribute the field before concluding, and pair every count
with the denominator.
