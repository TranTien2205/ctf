# Status, metrics, and info pages — operational checklist

server-status, phpinfo, /metrics, health endpoints: operational surfaces that leak internals — vhosts, loaded modules, request URLs, uptime internals.

## Checklist

- [ ] Probe: /server-status /nginx_status /phpinfo.php /info.php /metrics /health /status.
- [ ] server-status → vhost names, current request URLs (leaks hidden endpoints).
- [ ] phpinfo → document root, env vars, loaded modules, disable_functions.
- [ ] metrics → internal service names, queue names — a topology map.

## Abort conditions

- server-status request list leaks OTHER users' URLs — including tokens in query strings.
- phpinfo() prints _ENV — the same secrets as .env.
- A metrics page is a map for other attacks — capture the names.

## Falsifier

Falsifier — no status/info page exists or all are stripped to 'OK': the ops surface is closed.

## Cross-references

`debug-endpoints.md` · `env-config-leaks.md`
