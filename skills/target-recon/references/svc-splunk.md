# Service recon: splunk

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Splunk 8000: /en-US/account/login, /services/
server/info (needs auth, but the response shape = version
hints in errors), management :8089. The free-vs-enterprise
posture and default admin/changeme = documented check.
## Pivot

Signal harvested -> out-*; route named -> that skill.
