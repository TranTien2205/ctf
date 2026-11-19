# Chaining disclosure to impact — case catalogue

A disclosed artifact is never the flag — it's the key that reaches one. Every find routes to the class that owns its sink.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | JWT/session secret found | forge session | web-auth-session |
| 2 | Source code recovered | find the sink | white-box read |
| 3 | DB credentials | connect or SSRF | credential use |
| 4 | Internal endpoint named | probe it | the endpoint's class |
| 5 | Backup of the app | the handout offline | full white-box |
| 6 | Admin creds in config | login | auth flow |

## Falsifier

Falsifier — disclosed material reaches no privileged path: a finding with no chain is a hardening note, not a solve.

## Coverage notes

- A leaked secret that's already rotated is still evidence of the class, not impact.
- Don't stop at 'we found .env' — the chain is the point.

## Cross-references

`evidence.md` · `env-config-leaks.md`
