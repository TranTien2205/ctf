# Spring Actuator — the full endpoint map — checklist

Actuator's value isn't /env alone — it's the whole endpoint inventory: mappings, beans, configprops, heapdump, sessions.

## Checklist

- [ ] Enumerate every /actuator/<name> the root lists.
- [ ] env → secrets; mappings → all routes; configprops → full config.
- [ ] heapdump → download, strings, grep for passwords/keys/flag.
- [ ] beans → the dependency graph; httptrace → recent requests.

## Abort conditions

- Actuator paths differ between Boot 2/3 and configs — enumerate from the root.
- heapdump needs analysis tooling (strings + grep is enough for secrets).
- Some endpoints are write-capable (shutdown, restart) — read-only is the disclosure boundary.

## Falsifier

Falsifier — only health/info exposed and they're minimal: the rich endpoints are off.
