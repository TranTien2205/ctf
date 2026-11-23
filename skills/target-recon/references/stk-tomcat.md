# Stack playbook: tomcat

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Tomcat standalone: Server: Apache-Coyote/1.1,
JSESSIONID, /manager/html + /host-manager + /docs + /examples
defaults, error page 'Apache Tomcat/x.y.z' with version.

Recon checks:
- /manager/html -> basic-auth console = deploy surface
  (default creds = documented check)
- /examples/ -> servlet examples expose SnoopServlet info
- /manager/status -> runtime stats if reachable
- AJP :8009 presence -> smuggling class prior (Ghostcat)
- .war/.jsp upload surfaces in manager

Predicts: default-creds -> deploy rce class, info leak,
ajp smuggling/lfi (file-read-primitives).
## Pivot

Signal harvested -> out-*; route named -> that skill.
