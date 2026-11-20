# log_summary.py — the bracket+distribute tool

- `summary FILE` — lines, first/last lines, timestamp range,
  per-hour histogram, top-N IPs/users/paths/status, flag-like lines.
- `field FILE --regex REGEX` — a custom field distribution.
- `window FILE --around N` — context lines around line N.
The opening move before awk on the box.

## Why it exists

Hand-awk on a log with quoted fields is error-prone — summary does
the bracket and the standard distributions in one read, and window
gives context without a manual sed range.
