# Bundle and source-map mining

The front-end bundle is the only source a black-box challenge gives you —
and it routinely carries the endpoint list, feature flags, and the secrets the
backend never should have shipped. Mine it before probing anything else.

## Getting the sources

| Source | Get it |
|---|---|
| the bundle itself | `<script src>` in the HTML, `/_next/static/`, `/static/js/` |
| `.map` file | `<bundle-url>.map` — dev builds, staging, forgotten prod maps |
| inline maps | `//# sourceMappingURL=data:...` at the tail of the bundle |
| the framework's manifest | `/_buildManifest.js`, `/manifest.json`, webpack chunk list |

A `.map` restores the *original* source — file names, comments, even
`__SECRET__` placeholders. `tools/web/bundle_miner.py` extracts sourcesContent
from maps.

## What to grep for, in order of value

| Pattern | Finds |
|---|---|
| `["'](/api/[^"']+|https?://[^"']+)` | the endpoint map — every route the UI knows |
| `flag|secret|key|token|password` (case-insensitive) | shipped secrets, test creds |
| `process.env|import.meta.env|REACT_APP_|VITE_|NEXT_PUBLIC_` | baked-in env vars |
| `FeatureFlag|feature_|experimental|admin|debug` | hidden routes and flags |
| `JWT|alg:|private` | client-held signing material |
| `TODO|FIXME|XXX|HACK` | author's own annotations — often the bug |

The endpoint map feeds every downstream class: a route the UI calls but the
nav never links is a candidate for an access-control gap.

## Feature flags and hidden branches

Bundles ship dead code: `if (flags.beta)`, routes registered but never linked,
`role === "admin"` checks that gate only *visibility*. The check is client-side
— the endpoint behind it usually has no second gate.

```text
grep -o 'path:"[^"]*"' bundle.js      # every registered route
grep -o 'admin[^,}]*'  bundle.js      # admin-gated branches
```

Compare the registered routes against the ones the UI actually navigates —
the delta is the target list.

## Falsifier

The bundle is minified with no map, contains only framework boilerplate, and
no grep yields an endpoint, flag, or secret the recon didn't already know —
the front end carries nothing.

## Traps

- A `.map` on a CDN may be stale relative to the served bundle — check a
  `sourceMappingURL` comment and the bundle hash.
- Source content inside a map can include *more* than the deployed code —
  commented-out endpoints and `.env` values shipped by accident.
- A shipped API key is only a finding if it works — verify it against a
  read-only endpoint before claiming it.
