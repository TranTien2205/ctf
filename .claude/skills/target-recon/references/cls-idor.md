# Class recheck: idor

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon evidence web-idor needs: identifier shape per
resource (int/uuid/24hex/compound - idshape), the object
inventory reachable (own objects first), the ownership model
(how does the app know what is mine - session? token? path?),
and one same-object request across two accounts if creds
allow - the diff, not a verdict.
## Pivot

Signal harvested -> out-*; route named -> that skill.
