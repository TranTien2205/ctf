# Flag playbook — the gate-bypass runbook

## Step 1: extract the flags

```bash
grep -oE '(feature|features|flags|config|settings)\.[a-zA-Z_][a-zA-Z0-9_.]*' *.js | sort -u
grep -oE '(is[A-Z][a-zA-Z]+|has[A-Z][a-zA-Z]+|enabled|disabled|beta|admin|internal|debug)\s*[:=]' *.js | sort -u
grep -oE '(flags|features|FEATURES)\s*[:=]\s*\{[^{}]+\}' *.js
grep -oE 'localStorage\.[gs]etItem\(["'"'"'](flag|feature|debug|admin|beta)[^)]*' *.js
grep -oE 'meta\s*:\s*\{[^}]*requiresAuth[^}]*\}|can(Activate|Load)\s*:' *.js
```

## Step 2: name the gated endpoint

Each flag gates an endpoint or a code path — find it:

```bash
# the flag's context — the endpoint/logic it guards
grep -oE '.{100}(feature|flags)\.[a-zA-Z_.]+.{100}' *.js | head -20
grep -oE '(feature|flags)\.[a-zA-Z_.]+\s*[&|?]{1,2}\s*[^&|;]{0,60}' *.js
```

## Step 3: probe the gate — client or server?

```bash
# probe the gated endpoint directly — the falsifier
curl -s "$BASE$gated_ep" > g1
# is it public as-is?
head -c 100 g1
# if 403/401, try the flag shapes the client uses
curl -s "$BASE$gated_ep?debug=1&admin=1" > g2
curl -s -H "X-Debug: 1" -H "X-Admin: 1" "$BASE$gated_ep" > g3
```

- a `200` as-is → the gate was client-only → a finding →
  `web-logic-flaw`
- a `200` with a flag param/header → the flag reaches the gate →
  `web-logic-flaw`/`web-mass-assignment`
- a `403` that stays `403` → the server enforces → dead → record

## Step 4: the client-side-flag shapes

| How the client checks it | The bypass |
|---|---|
| `feature.X` gates a render | the endpoint is public — probe it |
| `meta.requiresAuth`/`PrivateRoute` | the gated endpoint is shipped — probe it |
| `localStorage.getItem('admin')` | set the storage flag or the param the client sends |
| a remote `featureService.get()` | the server may serve it — probe the flag service |
| `user.role==='admin'` | a `role`/`is_admin` param the server may trust |

## Step 5: route + record

- a client-gate bypass → `web-logic-flaw`/`web-idor`/`web-mass-assignment`
- a `role`/`is_admin` server-read param → `web-mass-assignment`
- a server-enforced gate → dead → record negative

## The rule

A client-side flag is a *lead* — it names a gate the server may not
enforce. The verify is the endpoint probe; the gate is real only if the
server checks it too.
