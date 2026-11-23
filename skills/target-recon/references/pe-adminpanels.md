# Path enum: adminpanels

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Admin-surface probes: /admin /administrator
/manage /management /dashboard /console /cp /phpmyadmin
/_admin /internal /staff. Response shape matters: 200=open,
302=redirect-to-login (exists but gated), 403=exists-denied,
404=absent - four DIFFERENT observations, each recorded.
## Pivot

Signal harvested -> out-*; route named -> that skill.
