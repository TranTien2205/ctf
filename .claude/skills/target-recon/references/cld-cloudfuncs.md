# Cloud recon: cloudfuncs

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Serverless surfaces: *.cloudfunctions.net,
*.lambda-url.*.on.aws, *.azurewebsites.net/api/,
cloudflare workers.dev - names in JS/docs/subdomains.
A function URL = narrow single-route target: web intake
against the function route directly.
## Pivot

Signal harvested -> out-*; route named -> that skill.
