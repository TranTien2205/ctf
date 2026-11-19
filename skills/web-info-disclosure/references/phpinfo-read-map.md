# Reading phpinfo() — the structured leak — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| phpinfo table rendered | full config | extract everything |
| _ENV/_SERVER rows | env vars | secrets and paths |
| Loaded modules list | module inventory | which attacks exist |
| disable_functions value | hardening level | what you CAN'T do |

## Falsifier

Falsifier — no phpinfo page exists: channel closed.
