# Stack playbook: spring

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Spring Boot fingerprints: Whitelabel error page,
JSESSIONID, X-Application-Context, /actuator endpoints.

Recon checks:
- GET /actuator -> endpoint list; env/heapdump/mappings/beans/
  configprops = the richest recon target that exists
- /actuator/mappings -> EVERY route + handler = surface map in
  one request
- /actuator/env -> property leak (secrets candidates)
- /actuator/heapdump -> memory dump = credential mining offline
- Whitelabel error -> Spring confirmed even without headers
- /swagger-ui or /v3/api-docs -> OpenAPI

Predicts: infodisclosure (actuator), massassign on @RequestBody
binding, sqli on raw JPA, ssti on Thymeleaf.
## Pivot

Signal harvested -> out-*; route named -> that skill.
