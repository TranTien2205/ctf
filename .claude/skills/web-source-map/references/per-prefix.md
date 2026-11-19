# Per-prefix — the env/config prefix semantics

## The framework env prefixes

Each framework marks client-public env values with a prefix — and devs
sometimes ship real secrets under the same prefix.

| Prefix | Framework | Marks |
|---|---|---|
| `REACT_APP_*` | create-react-app | client-public env |
| `NEXT_PUBLIC_*` | Next.js | client-public env |
| `VUE_APP_*` | Vue CLI | client-public env |
| `VITE_*` | Vite | client-public env |
| `GATSBY_*` | Gatsby | client-public env |
| `NUXT_ENV_*`/`publicRuntimeConfig` | Nuxt | client-public env |
| `import.meta.env.VITE_*` | Vite | client-public env |
| `process.env.REACT_APP_*` | CRA inlined | client-public env |
| `window.__CONFIG__`/`APP_ENV` | generic | a runtime config |

## The prefix trap

The prefix marks a value *intended* client-public — the client needs it.
It is a leak only if it carries a real secret — a private key, a
signing secret, a server credential — that should not be public.

- `NEXT_PUBLIC_API_URL` → config, not a leak
- `NEXT_PUBLIC_PRIVATE_KEY` → a finding
- `REACT_APP_API_KEY` → verify what it unlocks
- `VITE_SECRET` → verify what it signs

## The extraction

```bash
# every env-prefixed name
grep -oE '(REACT_APP|NEXT_PUBLIC|VUE_APP|VITE|GATSBY|NUXT)_[A-Z_]+' b.js | sort -u
# the values
grep -oE '(REACT_APP|NEXT_PUBLIC|VUE_APP|VITE)_[A-Z_]+("?\s*[:=]\s*"?)[^,"'\'']+' b.js | sort -u
# process.env reads
grep -oE 'process\.env\.[A-Z_a-z]+' b.js | sort -u
# the runtime config
grep -oE 'window\.__[A-Z_]+__\s*=\s*[^;]+' b.js
grep -oE '"runtimeConfig":\{[^}]+\}' entry.html
```

## The field priority

| Field suffix | Priority |
|---|---|
| `*_SECRET`, `*_PRIVATE_KEY`, `*_PASSWORD`, `*_TOKEN` | highest — a credential |
| `*_API_KEY`, `*_KEY`, `*_AUTH` | high — verify what it unlocks |
| `*_URL`, `*_ENDPOINT`, `*_HOST`, `*_INTERNAL` | high — an internal host |
| `*_DEBUG`, `*_TEST`, `*_DEV` | high — a debug flag |
| `*_FEATURE`, `*_FLAG`, `*_BETA` | medium — a feature gate |
| `*_VERSION`, `*_PUBLIC`, `*_THEME` | low — cosmetic |

## The verify rule per prefix

A prefixed value is config until it verifies as a secret — probe what
it authenticates/signs/unlocks. The prefix marks *intended* public;
the value decides *actual* leak.
