# API recon: authscheme

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Auth scheme inventory from 401/403 responses:
WWW-Authenticate: Bearer (JWT/oauth), Basic (base64 creds),
Digest, Negotiate; cookie session vs Authorization header
vs ?token= vs X-API-Key. The scheme names the session_dissect
input and the auth-class skill. Multiple schemes on different
paths = different trust boundaries worth mapping.
## Pivot

Signal harvested -> out-*; route named -> that skill.
