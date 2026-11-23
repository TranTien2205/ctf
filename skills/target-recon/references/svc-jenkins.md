# Service recon: jenkins

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Jenkins: /login default, X-Jenkins header on
responses, /script console (auth-gated), /api/json = job
inventory. Anonymous-read posture visible on /api/json
response. Version in footer. Routes to the admin-console
+ groovy-console priors.
## Pivot

Signal harvested -> out-*; route named -> that skill.
