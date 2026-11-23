# Worked example: domain-passive

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Walked: supplied <domain.tld>, no port.

1. pasv-crtsh: 4 SANs -> www., api., dev., static. subdomains;
   pasv-dnsrecords: A -> cloud provider CNAME (cld-providerid).
2. Live intake on https://<domain.tld> -> three-command set.
3. dev.<domain.tld> is a separate name -> vhost candidate
   (vh-sanenum): Host probe -> different response size =
   real second vhost (in-scope name).
4. Observations: provider=aws, vhosts=[www,api,dev],
   api. has /v1/ prefix shape.
5. classify on the api. surface first - the dev. name is a
   recorded lead, not a claim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
