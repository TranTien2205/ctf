# Flag and gate mining — the client-side feature switches

## The feature-flag surface

The client gates features behind flags — `feature.admin`, `config.debug`,
`flags.internal`, `beta`, `canary`, `enableX`. The UI checks the flag;
the server often does not. Mining the flags names the gated surface and
the endpoint behind it.

## The extraction

```bash
# flag/gate references
grep -oE '(feature|features|flags|config|settings)\.[a-zA-Z_][a-zA-Z0-9_.]*' bundle.js | sort -u
# gate checks
grep -oE '(is[A-Z][a-zA-Z]+|has[A-Z][a-zA-Z]+|can[A-Z][a-zA-Z]+|enabled|disabled|beta|admin|internal|debug)\s*[(:=]' bundle.js | sort -u
# a flags object
grep -oE '(flags|features|FEATURES|FLAGS)\s*[:=]\s*\{[^{}]+\}' bundle.js
# localStorage/remote flag source
grep -oE 'localStorage\.[gs]etItem\(["'"'"'](flag|feature|debug|admin|beta)[^)]*' bundle.js
```

## The gate shapes

| Gate shape | Meaning |
|---|---|
| `if (feature.X) showAdmin()` | a client-side gate — the admin code is shipped |
| `flags.Y ? render : null` | a render gate — the gated component is in the bundle |
| `config.debug && endpoint('/debug')` | a debug-gated endpoint call |
| `localStorage.getItem('admin')` | a flag the client reads from storage |
| a remote `featureService.get()` | a server-driven flag — the gate may be server-side |

## The flag → endpoint chain

The flag gates an *endpoint call* — the map names both. Setting the flag
(a request param `?admin=1`, a localStorage key, a header the client
sends, or the remote flag service) reaches the gated behavior IF the
server does not re-check.

## The falsifier — is the gate server-side?

The critical check: does the server enforce the gate? A client-side
`feature.admin` gate is bypassable; a server-side role check is not.
Probe the gated endpoint directly — a `403`/`401` that stays `403` even
with the flag set means the server enforces it; a `200` means the gate
was client-only.

## The client-only flag

A flag that gates a *render* but whose endpoint is public is still a
find — the endpoint was always reachable; the flag only hid it. The
map's job is to name the endpoint the flag hid; the class's job is to
use it.

## Route

| Flag/gate | Route |
|---|---|
| a gated endpoint that is public | `web-logic-flaw`/`web-idor` |
| a debug flag reaching a debug route | `web-logic-flaw`/`web-info-disclosure` |
| a remote flag service | `web-auth-session`/`web-logic-flaw` |
