# Service recon: mysql

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

MySQL handshake: the first server packet carries the
version string in cleartext (5.7.x, 8.0.x, MariaDB x.y) -
banner grab gives identity without auth. Native vs caching_sha2
plugin named in the handshake. Error on auth attempt reveals
host-access posture ('not allowed to connect').
## Pivot

Signal harvested -> out-*; route named -> that skill.
