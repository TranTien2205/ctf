# Recon checklist: authed

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Authenticated checklist (creds supplied): login
flow map (au-loginflow) -> session token shape ->
session_dissect -> post-auth surface map -> role/permission
boundaries (au-rolediff with second account if available)
-> id-space measurement -> privileged-route probes (403 vs
404 map) -> the whole weburl checklist re-run authed.
## Pivot

Signal harvested -> out-*; route named -> that skill.
