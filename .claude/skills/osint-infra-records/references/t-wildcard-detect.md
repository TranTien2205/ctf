# Detecting the wildcard

Query a random name `asdfqwer.<domain>` — if it resolves, a
wildcard exists and every brute-force "found" name needs a real
query to confirm it's distinct.

## The confirmation

A "found" name counts only if its answer differs from the
wildcard's (a different IP, or a distinct record) — otherwise it's
just the wildcard answering everything.
