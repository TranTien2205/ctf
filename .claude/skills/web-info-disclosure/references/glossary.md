# Glossary — disclosure vocabulary

| Term | Meaning here |
|---|---|
| catch-all | a fallback route returning the same 200 body for every path — the class's central falsifier |
| baseline | the response to a guaranteed-absent path; every probe diffs against it |
| loose object | a single .git object file (commit/tree/blob) fetchable over HTTP |
| pack-only | a .git with no loose objects — needs the pack protocol, git_dumper reports it honestly |
| sourcesContent | the embedded original sources inside a source map |
| actuator | Spring Boot's ops-endpoint family (/env, /mappings, /heapdump) |
| autoindex | the 'Index of /' directory listing page |
| swp | vim swap file — a crash-recovery copy of a source file |
| .DS_Store | macOS directory metadata listing real filenames |
| glue/pristine | SVN's stored original copies of working files |
| vhost | a named virtual host on the same IP — reachable by Host header |
| well-known | the /.well-known/ standard endpoint prefix |
| actuator/env | the Spring endpoint listing all environment properties |
| heapdump | a JVM memory dump endpoint — secrets via strings |
| jwks | the JSON Web Key Set endpoint — public signing keys |
| manifest | dependency declaration (package.json, composer.json, go.mod) |
| lockfile | pinned dependency versions (package-lock, composer.lock, go.sum) |
| disclosure chain | the path from an exposed artifact to an impact |
| bounded sweep | the ~15-20 canonical path list, run once, read carefully |
| hint-driven probe | a path probed only because evidence named it |
| partial exposure | a .git that serves refs but not objects — honest incompleteness |
| smart protocol | git's native fetch protocol — git clone works when it's on |
| Ignition/Whoops | Laravel's debug error renderer |
| yellow page | Django's DEBUG=True error page |
| X-Powered-By | framework version header — the cheapest fingerprint |
