# Chaining disclosure to impact

A disclosed artifact is never the flag — it's the key that reaches one. Every find routes to the class that owns its sink.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| JWT/session secret found | forge session | web-auth-session |
| Source code recovered | find the sink | white-box read |
| DB credentials | connect or SSRF | credential use |
| Internal endpoint named | probe it | the endpoint's class |
| Backup of the app | the handout offline | full white-box |
| Admin creds in config | login | auth flow |

## Steps

1. Classify each find: secret, source, endpoint, credential, path.
2. Route to the owning class: source→sink search, key→session forge, cred→login, endpoint→its class.
3. Record the disclosure as evidence, then work the chain — the disclosure alone is not impact.
4. The flag arrives through the chain, not the artifact.

## Falsifier

Falsifier — disclosed material reaches no privileged path: a finding with no chain is a hardening note, not a solve.

## Traps

- A leaked secret that's already rotated is still evidence of the class, not impact.
- Don't stop at 'we found .env' — the chain is the point.

## Cross-references

`evidence.md` · `env-config-leaks.md`
