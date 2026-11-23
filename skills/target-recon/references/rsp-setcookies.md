# Response reading: setcookies

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Set-Cookie reading: each cookie's name, flags
(HttpOnly/Secure/SameSite/path), shape (JWT dots, b64,
opaque), lifetime. Missing HttpOnly+Secure on session =
posture note; SameSite=Lax vs Strict changes csrf surface;
the cookie inventory is au-sessionissue's input.
## Pivot

Signal harvested -> out-*; route named -> that skill.
