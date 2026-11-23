# Cookie depth: shapemap

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Cookie-shape map per cookie: JWT (x.y.z dots),
itsdangerous (b64.b64.sig - flask/django signed), express
connect.sid (s%3A<val>.<sig>), rails _session (marshal or
aes), laravel (encrypted b64), PHPSESSID (opaque hex),
custom opaque. The shape names the forge-check - feed
session_dissect verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
