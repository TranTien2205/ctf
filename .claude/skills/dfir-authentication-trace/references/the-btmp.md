# btmp — attempt counts, not sources

btmp records failed logins — `ut_host` is the source per record; the
record count is attempts, so distinct-source questions dedupe on
ut_host.

## Attempts

Records are attempts; dedupe on ut_host.
## Dedupe

ut_host dedupes attempts to sources.
