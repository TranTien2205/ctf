# Stack playbook: rails

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Rails fingerprints: _<app>_session cookie (Marshal or
encrypted JSON), X-Runtime + X-Request-Id headers, /assets/
sprockets digests, CSRF meta tags.

Recon checks:
- GET /rails/info/routes -> full route table in dev mode =
  complete surface map in one request
- Cookie shape: --, Base64 chunks -> session_dissect handoff
- /up -> health route (Rails 7+)
- /assets/application-*.js -> front-end bundle harvest
- Error page 'We're sorry, but something went wrong' vs dev
  detailed exception -> env detection
- 422 on missing CSRF -> csrf enforcement posture

Predicts: massassign (strong params bypass attempts), idor on
integer ids, deserialization if Marshal session + known secret,
sqli on .where interpolation.
## Pivot

Signal harvested -> out-*; route named -> that skill.
