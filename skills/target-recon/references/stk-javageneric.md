# Stack playbook: javageneric

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Generic Java servlet: JSESSIONID, .jsp/.do/
.action extensions, /WEB-INF/ tree, Struts/Servlet behavior.

Recon checks:
- /WEB-INF/web.xml fetch attempts -> config map (rarely open)
- .action/.do -> Struts = ogln injection class weight
- /manager/html -> Tomcat manager = default-creds surface
- Error 'Apache Tomcat/x.y' -> version fingerprint
- .jsp upload surfaces -> jsp webshell class
- AJP connector 8009 style -> smuggling class notes

Predicts: deserialization, sqli, file-upload webshell,
struts-specific cmdi, infodisclosure.
## Pivot

Signal harvested -> out-*; route named -> that skill.
