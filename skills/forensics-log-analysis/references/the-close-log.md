# Closing — the log-analysis discipline

Bracket the file, distribute the field, find the outlier, window
the context. The verbatim line + the count that makes it anomalous
is the evidence; a uniform log is the falsifier.

## The one-line method

wc -l and head/tail → sort|uniq -c the field → window the hit →
quote it with its count. Everything else is a variation on that.
