# Config mining — the build-inlined configuration surface

## Why config is gold

The build inlines environment config into the bundle — API bases, keys,
flags, hosts, feature toggles. It is the single densest secret/flag
surface because it is *meant* to carry config and devs put real
credentials under "config".

## The config carriers

| Carrier | Shape |
|---|---|
| `config.js` / `env.js` | a standalone config script |
| `process.env.*` / `DefinePlugin` | inlined env values |
| `REACT_APP_*` / `NEXT_PUBLIC_*` / `VUE_APP_*` / `VITE_*` | framework env prefix |
| `__NEXT_DATA__.runtimeConfig` | Next serialized config |
| `window.__CONFIG__` / `window.APP_ENV` | a runtime-injected config |
| `import.meta.env.*` | Vite env refs |
| a `config`/`settings`/`defaults` object | an app config literal |

## The extraction

```bash
# env-prefixed names
grep -oE '(REACT_APP|NEXT_PUBLIC|VUE_APP|VITE|GATSBY|NUXT)_[A-Z_]+' bundle.js | sort -u
# process.env reads
grep -oE 'process\.env\.[A-Za-z_]+' bundle.js | sort -u
# a config object literal
grep -oE '(config|env|settings|defaults|CONSTANTS)\s*[:=]\s*\{[^{}]{20,}' bundle.js
# window-injected
grep -oE 'window\.__[A-Z_]+__\s*=\s*[^;]+' bundle.js
# Next runtimeConfig
curl -s "$BASE/" | grep -oE '"runtimeConfig":\{[^}]+\}'
```

## The config-field priority

| Field | Priority |
|---|---|
| `apiKey`, `secret`, `token`, `privateKey`, `clientSecret` | highest — a credential |
| `apiUrl`, `baseUrl`, `endpoint`, `internal` | high — an internal host/route |
| `debug`, `verbose`, `testMode`, `dev` | high — a debug gate |
| `feature.*`, `flag.*`, `enable.*`, `beta` | high — a feature gate |
| `admin`, `internal`, `hidden` | medium — a gated surface |
| `version`, `public`, `theme`, `locale` | low — cosmetic |

## The `NEXT_PUBLIC_` trap

The `NEXT_PUBLIC_`/`REACT_APP_`/`VITE_` prefix marks a value as *client-
public by design* — it is shipped on purpose. It is a leak only if it
carries a real secret (a private key, a signing secret) that should not
be public. A `NEXT_PUBLIC_API_URL` is config; a
`NEXT_PUBLIC_PRIVATE_KEY` is a finding. Verify what it unlocks.

## The debug/dev config

`debug: true`, `NODE_ENV: "development"`, `testMode` — a dev config in a
prod bundle signals a lax build and often a dev endpoint or debug route
still reachable. Route to `web-logic-flaw`/`web-info-disclosure`.
