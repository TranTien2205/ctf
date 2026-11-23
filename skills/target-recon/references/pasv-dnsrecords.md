# Passive recon: dnsrecords

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

dig the supplied domain: A/AAAA for the real
origin (behind a CDN it may differ), CNAME for cloud provider,
TXT for SPF/verification tokens (google-site-verification,
MS=, DKIM selectors) = infra identity signals, MX/NS for
provider. CNAME -> *.herokuapp.com / *.cloudapp.net names the
platform. Each record is an observation line for out-*.
## Pivot

Signal harvested -> out-*; route named -> that skill.
