# The timestamp field — the timezone trap

A timestamp-only grep misses the timezone story — check which zone
the log records (UTC vs local) before answering "when". The
per-hour histogram in log_summary.py shows the burst.

## The zone check

The first line's timestamp vs the file's metadata (or a known
event) reveals the zone. UTC is the server norm; a challenge may
use a named zone deliberately.

## The burst

A spike in the per-hour count is the attack window; the lines in
that window carry the story.
