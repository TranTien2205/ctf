# Service recon: ldap

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

LDAP: anonymous bind attempt + rootDSE query - naming
contexts, vendorName, vendorVersion come back without creds
when anonymous reads are on. dc= structure = the directory map.
A 389/636 port is directory surface -> the auth/sqli-ldap
depth.
## Pivot

Signal harvested -> out-*; route named -> that skill.
