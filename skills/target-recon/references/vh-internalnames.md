# Vhost/subdomain: internalnames

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Internal-name harvest: SANs, PTR records,
cert subjects, error-page links, redirect Location headers,
HTML canonical/OG tags naming internal FQDNs. dev.corp.local
and staging.* on the same IP = in-scope vhost candidates;
recorded verbatim with the source they came from.
## Pivot

Signal harvested -> out-*; route named -> that skill.
