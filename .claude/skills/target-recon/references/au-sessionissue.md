# Authenticated recon: sessionissue

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Session issue capture: what the server sets
post-auth - cookie name/shape/flags (HttpOnly, Secure,
SameSite), token format (JWT dots, itsdangerous chunks,
opaque hex), expiry behavior, rotation on privilege change.
The verbatim Set-Cookie line + decoded token shape goes to
session_dissect - recon names WHAT the session is, the tool
says whether it is forgeable.
## Pivot

Signal harvested -> out-*; route named -> that skill.
