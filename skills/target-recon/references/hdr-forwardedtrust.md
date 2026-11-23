# Header depth: forwardedtrust

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Forwarded-header trust map: send a
controlled X-Forwarded-For/Host/Proto and watch for
behavior change (content, redirects, errors) - which
forwarded headers the app trusts = parser-differential
prior + ssrf/host-header surfaces. Record accepted vs
ignored verbatim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
