# Status, metrics, and info pages — case catalogue

server-status, phpinfo, /metrics, health endpoints: operational surfaces that leak internals — vhosts, loaded modules, request URLs, uptime internals.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /server-status Apache page | Apache status | vhosts, current requests |
| 2 | /phpinfo.php or phpinfo output | full PHP config | env, paths, modules |
| 3 | /metrics with prometheus format | metrics exposed | internal names |
| 4 | /health or /status with internals | health detail | dependency map |

## Falsifier

Falsifier — no status/info page exists or all are stripped to 'OK': the ops surface is closed.

## Coverage notes

- server-status request list leaks OTHER users' URLs — including tokens in query strings.
- phpinfo() prints _ENV — the same secrets as .env.
- A metrics page is a map for other attacks — capture the names.

## Cross-references

`debug-endpoints.md` · `env-config-leaks.md`
