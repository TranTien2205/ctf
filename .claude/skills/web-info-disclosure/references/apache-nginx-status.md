# Apache server-status and nginx stub_status

The classic /server-status (mod_status) and nginx stub_status: request lists leak other users' URLs — including tokens.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /server-status HTML page | mod_status | vhosts + current requests |
| request table with URLs | live request URLs | hidden endpoints/tokens |
| /nginx_status or stub_status | connection stats | less detail |

## Steps

1. Probe /server-status /nginx-status /status.
2. The request table shows live URLs other clients fetched — tokens and hidden endpoints.
3. Vhost names reveal internal sites.
4. Sample over time — a busy server's table rotates.

## Falsifier

Falsifier — status pages 404/403 or stripped: closed.

## Traps

- The interesting rows are OTHER clients' requests — grep the table.
- mod_status with ExtendedStatus shows query strings — where tokens live.
- A 403 on server-status is common; try the other verbs/Host tricks.

## Commands

```bash
curl -s '$BASE/server-status' | grep -oE 'GET [^ ]+|POST [^ ]+' | sort -u | head
```

## Cross-references

`status-pages.md`
