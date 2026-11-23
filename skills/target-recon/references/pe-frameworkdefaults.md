# Path enum: frameworkdefaults

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Framework-default path probes per
identified stack - the stk-* playbooks carry the lists:
/wp-json/wp/v2/users (WP), /admin/ (Django), /actuator
(Spring), /rails/info/routes, /_ignition (Laravel), /elmah.axd
(.NET), /debug/pprof (Go). One probe each, status recorded.
## Pivot

Signal harvested -> out-*; route named -> that skill.
