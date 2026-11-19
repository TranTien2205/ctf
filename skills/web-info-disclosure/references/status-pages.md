# Status, metrics, and info pages

server-status, phpinfo, /metrics, health endpoints: operational surfaces that leak internals — vhosts, loaded modules, request URLs, uptime internals.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /server-status Apache page | Apache status | vhosts, current requests |
| /phpinfo.php or phpinfo output | full PHP config | env, paths, modules |
| /metrics with prometheus format | metrics exposed | internal names |
| /health or /status with internals | health detail | dependency map |

## Steps

1. Probe: /server-status /nginx_status /phpinfo.php /info.php /metrics /health /status.
2. server-status → vhost names, current request URLs (leaks hidden endpoints).
3. phpinfo → document root, env vars, loaded modules, disable_functions.
4. metrics → internal service names, queue names — a topology map.

## Falsifier

Falsifier — no status/info page exists or all are stripped to 'OK': the ops surface is closed.

## Traps

- server-status request list leaks OTHER users' URLs — including tokens in query strings.
- phpinfo() prints _ENV — the same secrets as .env.
- A metrics page is a map for other attacks — capture the names.

## Commands

```bash
for p in /server-status /phpinfo.php /metrics /health; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`debug-endpoints.md` · `env-config-leaks.md`
