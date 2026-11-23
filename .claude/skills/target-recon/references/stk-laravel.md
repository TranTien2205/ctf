# Stack playbook: laravel

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Laravel fingerprints: laravel_session + XSRF-TOKEN
cookies, blade-rendered pages, /vendor/ asset paths in errors.

Recon checks:
- GET /.env -> APP_KEY + DB creds leak (common CTF gift)
- GET /_ignition/health-check -> Ignition debug = file-read/RCE
  class surface when APP_DEBUG
- /telescope, /horizon -> debug dashboards = full request log
- Exception 'Whoops' page -> stack + env leak
- /api/* route shapes, sanctum vs passport token style
- APP_DEBUG + leaked APP_KEY -> session forge class

Predicts: infodisclosure (.env), deserialization with known
APP_KEY, sqli on raw where clauses, idor on model ids.
## Pivot

Signal harvested -> out-*; route named -> that skill.
