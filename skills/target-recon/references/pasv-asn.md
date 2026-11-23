# Passive recon: asn

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

ASN/netblock recon: whois -h whois.cymru.com ' -v
<ip>' or the web UI -> AS number + netblock name + route.
Names the hosting org (AWS/DigitalOcean/university/ISP) and
the netblock size = infra identity. A /32 route = a single
purpose-built host = CTF-instance shape.
## Pivot

Signal harvested -> out-*; route named -> that skill.
