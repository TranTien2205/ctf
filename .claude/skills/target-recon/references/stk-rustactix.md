# Stack playbook: rustactix

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Rust actix/axum: minimal headers (none by
default), awc client quirks, /metrics common when prometheus
middleware, error bodies plain text.

Recon checks:
- Bare error pages -> actix-web identity via error strings
- /metrics prometheus -> endpoint+version leak
- JSON acceptance -> serde validation errors name fields
- Route conventions -> kebab-case REST
- No session default -> token/api-key auth posture

Predicts: logic flaws, sqli via diesel raw, idor.
## Pivot

Signal harvested -> out-*; route named -> that skill.
