# Stack playbook: weblogic

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

WebLogic: /console/ admin, T3 protocol on :7001,
X-Powered-By absent but Server: WebLogic, .jspa/jsf pages,
wls-wsat endpoints.

Recon checks:
- /console/ -> admin login = the classic surface
- /wls-wsat/CoordinatorPortType -> XMLDecoder surface
  (the notorious deserialization endpoint)
- T3 banner grab :7001 -> binary protocol presence
- /uddiexplorer/ -> ssrf surface prior
- Error pages -> version string leak

Predicts: java deserialization, ssrf, admin-console,
file-read.
## Pivot

Signal harvested -> out-*; route named -> that skill.
