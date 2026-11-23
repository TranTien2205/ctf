# Authenticated recon: loginflow

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Login flow mapping: identify the auth endpoint
(POST /login, /auth, /api/session, /oauth/token), the credential
format (json user/pass, form-encoded, nested objects), the
success signal (Set-Cookie vs JSON token vs redirect), the
failure signal (status, message shape, timing - userenum
surface). Lockout/rate-limit headers on failed attempts are
recorded before any further attempt.
## Pivot

Signal harvested -> out-*; route named -> that skill.
