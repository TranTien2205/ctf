# Worked — a SAN sibling

1. `--crtsh` → a SAN `internal.flag.example.com`.
2. Query/visit that host → the next step or the flag.
The cert names the host the challenge never gave you.

## Notes

- A wildcard SAN (`*.domain`) doesn't name a specific host —
  ignore it for sibling hunting.
- An internal/staging/dev SAN is a real candidate — query it.
- The SAN came from certificate transparency — public data.

## The confirm

A SAN that names an internal/flag host is the lead — confirm by querying it; the SAN itself is the measurement of what was issued.

## Common SAN shapes

internal., dev., staging., admin., flag., secret., backup., mail. — the non-public prefixes are the candidates.
