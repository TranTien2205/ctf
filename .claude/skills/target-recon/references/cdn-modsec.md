# CDN/WAF identity: modsec

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

ModSecurity WAF: 406/403 on probe patterns with
plain 'Not Acceptable' or mod_security text, OWASP CRS rule
ids in error bodies, cookie-less request blocking. Detected
by one calibrated probe (a quote in a param) - the block
page shape is the fingerprint, recorded verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
