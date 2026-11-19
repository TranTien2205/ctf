# Reading phpinfo() — the structured leak — case catalogue

phpinfo() is the single densest disclosure page in PHP apps: env vars, paths, modules, loaded config, version details.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | phpinfo table rendered | full config | extract everything |
| 2 | _ENV/_SERVER rows | env vars | secrets and paths |
| 3 | Loaded modules list | module inventory | which attacks exist |
| 4 | disable_functions value | hardening level | what you CAN'T do |

## Falsifier

Falsifier — no phpinfo page exists: channel closed.
