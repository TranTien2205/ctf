# Skills

Open **one** depth skill at a time. The method in a depth skill is written to be
read while the target is in front of you, and opening three at once both burns
the context window and anchors the next hypothesis before the surface is mapped.

| Skill | Open it when |
|---|---|
| `blackbox-web` | an engagement is starting or resuming — read this one first |
| `orchestration` | deciding which model does what, or writing a plan |
| `web-sqli` | a parameter may reach a SQL query |
| `web-command-injection` | a parameter may reach a shell |
| `web-file-read` | a parameter names a file, template, locale or attachment |
| `web-ssti` | a value is rendered by a template engine |
| `web-authz` | an id or a tenant key decides whose data comes back |
| `web-auth-session` | a token or a session decides whether the request is allowed at all |
| `web-ssrf` | a parameter takes a URL, host or webhook |
| `web-xss` | a value is reflected into a page |
| `web-xxe` | an endpoint parses XML, or anything built on XML |
| `web-deserialization` | a parameter carries a serialized object |
| `web-nosqli` | a parameter reaches a document store or a JSON query |
| `web-race-condition` | two requests at once might reach a window one cannot |
| `web-secret-exposure` | a credential appears somewhere it should not |
| `cve-triage` | a scanner matched, or a version has known CVEs |
| `report-writing` | the engagement is ending |
| `extending-argus` | a class, ladder, CVE script, tool or model profile needs adding |

## Classes with a ladder but no depth skill yet

`graphql-exposure`, `cache-poisoning`, `csrf`, `prototype-pollution`,
`open-redirect`, `file-upload-rce`, `log4shell`.

Every one of them has a proof requirement in the matrix (`argus proof <class>`)
and a probe ladder (`knowledge.playbook vuln_class=<class>`) whose last rung
names the tool that can satisfy that requirement. That is enough to work the
class correctly; what is missing is the written-down method — the shapes that
look like a finding and are not — and the `extending-argus` skill says how to
add it.

Stating this list is deliberate. A skills directory that looks complete when it
is not is worse than a short one that says where it ends.
