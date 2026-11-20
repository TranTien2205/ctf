# Evidence detail — what to quote

- The verbatim record string (a TXT, a SAN, an IP).
- The resolver/server that answered.
- The TTL + the query date.
- The source (live query vs crt.sh vs archive).

## The packet

The record answer verbatim, the server/resolver, the TTL, the
query date, and which source it came from — so the answer is
reproducible and dated.

## Lead vs measurement

A record that names a host is a lead; the flag read from that host is the measurement. Do not claim a flag from a record that only names where it lives.

## The quote

The record verbatim + the resolver + the TTL + the source + the date — reproducible and dated.

## Reproducible

The answer must be re-derivable — record the resolver + TTL + date so another query confirms it.
