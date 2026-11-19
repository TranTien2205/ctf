# Apache server-status and nginx stub_status — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /server-status HTML page | mod_status | vhosts + current requests |
| request table with URLs | live request URLs | hidden endpoints/tokens |
| /nginx_status or stub_status | connection stats | less detail |

## Falsifier

Falsifier — status pages 404/403 or stripped: closed.
