# Chaining disclosure to impact — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| JWT/session secret found | forge session | web-auth-session |
| Source code recovered | find the sink | white-box read |
| DB credentials | connect or SSRF | credential use |
| Internal endpoint named | probe it | the endpoint's class |
| Backup of the app | the handout offline | full white-box |
| Admin creds in config | login | auth flow |

## Falsifier

Falsifier — disclosed material reaches no privileged path: a finding with no chain is a hardening note, not a solve.
