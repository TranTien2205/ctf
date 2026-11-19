# Structure mining — the file names as a map of the app

## What the structure gives

Even without `sourcesContent`, a map's `sources` array lists every
original file path — the app's internal layout. `src/api/auth.js`,
`src/config/secrets.js`, `src/admin/`, `src/utils/crypto.js` — the
names alone are leads.

## The layout read

```bash
# every source path in a map
python3 -c "import json; m=json.load(open('m.js.map')); print('\n'.join(m['sources']))" | sort -u
```

Group them: `api/` (server call layer), `config/`/`env/` (config +
secrets), `admin/`/`internal/`/`private/` (gated code), `utils/`/
`crypto`/`auth` (security logic), `components/` (UI).

## The high-value path prefixes

| Prefix | Signals |
|---|---|
| `src/config/`, `src/env/`, `src/constants/` | config + secrets |
| `src/api/`, `src/services/` | the endpoint layer |
| `src/admin/`, `src/internal/`, `src/private/` | gated code |
| `src/auth/`, `src/crypto/`, `src/security/` | the security logic |
| `src/utils/`, `src/helpers/` | helpers — often the sink |
| `node_modules/` | dependencies — skip |

## The hosted-path probe

Some deployments serve the original files at their source paths —
`/src/config/secrets.js`, `/static/src/api/auth.js`. Probe the
`sources` paths against the host:

```bash
for p in $(python3 -c "import json;print('\n'.join(json.load(open('m.js.map'))['sources']))"); do
  p=${p#webpack://*/}; p=${p#/}
  curl -s -o /dev/null -w '%{http_code} ' "$BASE/$p"; echo "$p"
done | grep -v '^404'
```

A `200` on a source path returns the original file — the map without
the map.

## The structure → file-read lead

The layout names files that may also be reachable through a
`file-read-primitives` or `web-info-disclosure` surface — a
`src/config/secrets.js` in `sources` is a target for a `/src/` or
`/.env`-style probe even if the map has no content.

## The naming as intent

File names carry intent — `admin.js`, `secret.js`, `internal-api.js`,
`debug-panel.js`, `flag.js`, `bypass.js`. A file *named* for the
interesting thing is a strong lead even with no content.
