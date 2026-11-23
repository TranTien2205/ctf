# TLS recon: certfields

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Certificate field harvest: subject CN, issuer
(self-signed vs CA), validity dates (fresh cert = fresh
infra), key type/size. openssl s_client -connect host:port
</dev/null | openssl x509 -noout -subject -issuer -dates.
Self-signed on a CTF instance = normal; a corporate issuer on
a challenge port = the odd observation.
## Pivot

Signal harvested -> out-*; route named -> that skill.
