# Workflow map — the pass as a decision tree

## The top-level tree

```
SPA ships a bundle?
  ├─ no  -> not this route (server-rendered, no client logic)
  └─ yes -> enumerate EVERY bundle + the manifest
              │
              ▼
         for each bundle: map probe (4 routes)
              │
       ┌──────┴──────┐
       │             │
   map found?    map absent / catch-all
       │             │
  sourcesContent?    └─> string mine EVERY bundle
       │                    (endpoints, params,
   ┌───┴───┐                secrets, flags, routes)
   │       │
  yes     no
   │       │
   ▼       ▼
reconstruct  structure only
source       (file names)
   │
   ▼
read source: sinks, keys, comments, flag

              │
              ▼
        TRIAGE the leads
              │
              ▼
        VERIFY each live
              │
   ┌──────────┼──────────┐
   │          │          │
 live       dead      unverifiable
   │          │          │
   ▼          ▼          ▼
 route to   record    route to a
 its class  negative  reach class
```

## The decision rows

| At | If | Then |
|---|---|---|
| inventory | a lazy/admin chunk in the manifest | fetch + mine it |
| map | `.map` `200 json` `{"version":3` | reconstruct |
| map | `.map` `200 text/html` | a catch-all — string mine |
| map | `sourcesContent` null | structure leads only |
| mine | a live secret | `web-auth-session` |
| mine | a hidden endpoint | verify → its class |
| mine | a feature flag | probe the gated endpoint |
| mine | an internal host | `web-ssrf` |
| mine | a flag shape | `pre-flag` |
| verify | endpoint 404 | dead — record |
| verify | endpoint 200 non-index | real → its class |
| verify | secret authenticates | `web-auth-session` |
| verify | flag server-enforced | dead — record |
| end | all leads dead | the route is dead — record + next layer |

## The loop-back points

- a lazy chunk found in the manifest → back to inventory for it
- a recovered source naming an endpoint → back to verify
- a `.map` presence → the adjacent-disclosure probe (`.git`, `.env`)

## The stop conditions

- every lead verified-or-dead → recon done; the exploit is the routed
  class
- every lead dead + opaque strings + no map → the route is dead —
  record + move to `.git`/`.env`/`web-triage`
- a flag candidate → `pre-flag`; submit if it passes
