# Path enum: envvariants

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Env-file probes: /.env /.env.local /.env.prod
/.env.development /env /config/.env /.env.bak. Dotfile blocking
(.ht*) on Apache returns 403 for .env too - record the status
verbatim; nginx usually 404s unless exposed. Any 200 = secrets
observation.
## Pivot

Signal harvested -> out-*; route named -> that skill.
