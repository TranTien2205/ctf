# Stack playbook: jboss

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

JBoss/WildFly: /jmx-console /admin-console /web-console
defaults, JSESSIONID, 'JBoss'/'WildFly' banners, :9990 mgmt.

Recon checks:
- /jmx-console/ -> MBean inventory = the classic surface
- /admin-console/ + :9990 -> management
- /invoker/JMXInvokerServlet -> deserialization prior
- Deployment scanner endpoints
- Error stack -> version

Predicts: deserialization, admin-console, deploy surface.
## Pivot

Signal harvested -> out-*; route named -> that skill.
