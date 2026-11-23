# Stack playbook: gogeneric

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Go service: minimal headers (often none),
/debug/pprof when net/http/pprof imported, prometheus /metrics,
chi/gin/echo routing.

Recon checks:
- GET /debug/pprof/ -> full runtime introspection = recon gold
  (goroutine stacks, heap, cmdline!)
- /metrics -> prometheus: internal names, versions, endpoints
- /debug/pprof/cmdline -> binary path + args
- No Server header -> net/http default style confirmed by
  error format
- /swagger or /openapi.json when swag generated

Predicts: infodisclosure (pprof, metrics), template injection
rare, sqli on database/sql concat, idor.
## Pivot

Signal harvested -> out-*; route named -> that skill.
