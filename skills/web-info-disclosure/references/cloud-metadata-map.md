# Cloud metadata and internal endpoints — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /latest/meta-data or 169.254.169.254 reachable | metadata exposed | cloud creds |
| internal admin port on the same host | misconfigured exposure | probe |
| kubernetes/azure/gcp metadata paths | platform metadata | read tokens |

## Falsifier

Falsifier — no cloud signature in headers and no internal endpoint surface: out of scope for this class.
