# CDN/WAF identity: akamai

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Akamai identity: x-akamai-transformed, akamai-*
headers, server: AkamaiGHost, True-Client-IP handling.
Reference-interception behavior on headers is a parser-
differential class note. The staged 'ghost' error pages
fingerprint it without headers.
## Pivot

Signal harvested -> out-*; route named -> that skill.
