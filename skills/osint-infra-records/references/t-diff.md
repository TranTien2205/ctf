# Diffing over time

Re-query after a TTL — a changed answer (an IP, a new SAN) is a
signal; passive DNS + archive corroborate what changed.

## The method

- Note the answer + TTL at first query.
- Re-query after the TTL — did it change?
- Passive DNS shows the historical values.
- A newly-appearing SAN or a moved IP is the signal.
