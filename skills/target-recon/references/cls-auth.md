# Class recheck: auth

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Recon evidence web-auth-session needs: session token
shape (JWT dots/itsdangerous/opaque - session_dissect input),
issue/rotation/expiry behavior (au-sessionissue), lockout
signals on failed login, password-reset token delivery shape,
remember-me handling, and the auth scheme per route group.
## Pivot

Signal harvested -> out-*; route named -> that skill.
