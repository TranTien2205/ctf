# Apache server-status and nginx stub_status — checklist

The classic /server-status (mod_status) and nginx stub_status: request lists leak other users' URLs — including tokens.

## Checklist

- [ ] Probe /server-status /nginx-status /status.
- [ ] The request table shows live URLs other clients fetched — tokens and hidden endpoints.
- [ ] Vhost names reveal internal sites.
- [ ] Sample over time — a busy server's table rotates.

## Abort conditions

- The interesting rows are OTHER clients' requests — grep the table.
- mod_status with ExtendedStatus shows query strings — where tokens live.
- A 403 on server-status is common; try the other verbs/Host tricks.

## Falsifier

Falsifier — status pages 404/403 or stripped: closed.
