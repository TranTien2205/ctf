# Recon checklist: hostport

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

host:port checklist: banner GET first - HTTP?
-> weburl checklist. Not HTTP -> nc banner grab -> svc-*
match by banner/prompt -> interactive? pwn-binary-triage
route. TLS? openssl cert harvest first. Unknown -> protocol
probes (newline, HELP, binary). Silent -> recorded
resolves-but-silent negative.
## Pivot

Signal harvested -> out-*; route named -> that skill.
