# Apache server-status and nginx stub_status — case catalogue

The classic /server-status (mod_status) and nginx stub_status: request lists leak other users' URLs — including tokens.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /server-status HTML page | mod_status | vhosts + current requests |
| 2 | request table with URLs | live request URLs | hidden endpoints/tokens |
| 3 | /nginx_status or stub_status | connection stats | less detail |

## Falsifier

Falsifier — status pages 404/403 or stripped: closed.
