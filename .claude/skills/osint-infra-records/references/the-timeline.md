# The timeline — records over time

SOA serial + passive-DNS + archive captures place a domain's
records in time — when a host appeared, when an IP changed; the
"when" answer may live in history, not the live records.

## The sources

- SOA serial — a date-ish zone version.
- Passive DNS — historical resolutions.
- archive.org — the site's past content.
- Cert issuance dates — when a SAN first appeared.

## When it matters

A SAN that no longer resolves, a moved IP, a deleted record — history answers what once was.
