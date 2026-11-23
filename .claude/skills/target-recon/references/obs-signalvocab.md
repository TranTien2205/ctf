# Handoff format: signalvocab

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Signal vocabulary for the handoff: stack
(server/powered-by/framework/cookie-shape), surface
(endpoints, params, methods), oddity (debug, exposed-file,
version-leak), posture (tls, waf, ratelimit, auth-scheme).
Naming observations in this vocabulary = they land as
classify signals directly.
## Pivot

Signal harvested -> out-*; route named -> that skill.
