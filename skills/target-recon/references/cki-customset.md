# Cookie depth: customset

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Custom cookie inventory: app-named cookies
(role=, admin=, user_id=, prefs=) beyond the session id -
plaintext value cookies are free parameters (pd-cookieparams);
signed-looking ones go to session_dissect first.
## Pivot

Signal harvested -> out-*; route named -> that skill.
