# Cookie depth: flagmatrix

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Cookie-flag matrix per cookie: HttpOnly
(xss can't read it), Secure (https only), SameSite (csrf
surface by value), Path/Domain scope, Expires (session vs
persistent). Missing flags on session cookies = posture
observations - verbatim per cookie.
## Pivot

Signal harvested -> out-*; route named -> that skill.
