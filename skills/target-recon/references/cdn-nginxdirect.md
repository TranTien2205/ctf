# CDN/WAF identity: nginxdirect

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Direct nginx (no CDN): server: nginx[/x.y],
no cf-*/x-amz-*/akamai- headers, connection timing differs
from edge-fronted. A versioned banner = version signal.
nginx behind a load balancer shows via/X-Forwarded chains -
each hop recorded as the topology map.
## Pivot

Signal harvested -> out-*; route named -> that skill.
