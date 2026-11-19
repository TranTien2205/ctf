# Internal vhosts and loopback-only routes — case catalogue

Routes that exist only on internal hostnames or the loopback interface — disclosure finds them named in configs/comments.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | config/comment names an internal host | a vhost exists | Host-probe it |
| 2 | route present in source but 404s externally | loopback-only | backend-fetch chain |
| 3 | admin.* or dev.* subdomain in cert/comment | subdomain surface | probe it |

## Falsifier

Falsifier — no internal names exist in any leaked material: nothing to probe.
