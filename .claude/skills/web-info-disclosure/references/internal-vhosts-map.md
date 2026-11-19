# Internal vhosts and loopback-only routes — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| config/comment names an internal host | a vhost exists | Host-probe it |
| route present in source but 404s externally | loopback-only | backend-fetch chain |
| admin.* or dev.* subdomain in cert/comment | subdomain surface | probe it |

## Falsifier

Falsifier — no internal names exist in any leaked material: nothing to probe.
