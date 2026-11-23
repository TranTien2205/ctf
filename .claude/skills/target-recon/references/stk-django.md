# Stack playbook: django

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Django fingerprints: sessionid + csrftoken cookie pair,
/admin/ login page 'Log in | Django site admin', Werkzeug-style
dev error pages, /static/ served paths.

Recon checks:
- GET /admin/ -> Django admin present (login + version in footer
  sometimes)
- csrftoken cookie + CSRF token in forms -> framework confirmed;
  csrf class weight on state-changing routes
- DEBUG error pages (yellow traceback) -> source-path and config
  leak = infodisclosure, plus SECRET_KEY guesses later
- /accounts/login/, /api/ root -> endpoint style
- ALLOWED_HOSTS disallowed-host error -> host-header behavior
- __debug__/ or django-debug-toolbar URLs -> debug surface

Predicts: sqli via raw queries, ssti rare (Django templates
sandbox), idor on int PKs (sequential default), authz via
/admin misconfigured or staff endpoints.
## Pivot

Signal harvested -> out-*; route named -> that skill.
