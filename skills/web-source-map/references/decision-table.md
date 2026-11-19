# Decision table — every state and its next action

## The discovery decisions

| State | Action |
|---|---|
| entry page has `<script src>` | enumerate every script + manifest |
| no app `.js` | not this route — server-rendered |
| Next.js fingerprint | fetch `_buildManifest.js` for the route list |
| a manifest exists | enumerate every lazy chunk |
| `.map` `200 json` `{"version":3` | reconstruct `sourcesContent` |
| `.map` `200 text/html` | a catch-all — string mine |
| `.map` 404 everywhere | string mine every bundle |
| `sourcesContent` null | structure leads only |

## The mining decisions

| Found | Action |
|---|---|
| an endpoint string | `curl` live → real → its class; 404 → record |
| a secret candidate | `Authorization`/decode → live → auth-session; dead → record |
| a feature flag | probe the gated endpoint → client gate → logic |
| an internal host | route to `web-ssrf` |
| a param name | pair with its endpoint → its class |
| a route path | probe `/api/` prefix → server path or client-only |
| a `sources` path | probe the hosted `/src/` path |
| a GraphQL endpoint | `web-graphql` |
| a flag shape | `pre-flag` |
| a recovered-source sink | its class |
| a `.map` presence | probe `.git`/`.env`/backups |
| a lazy/admin chunk | fetch + mine it |
| a `role`/`is_admin` param | `web-mass-assignment` |

## The verify decisions

| Result | Verdict | Next |
|---|---|---|
| endpoint `200`/`401`/`403`/`405` non-index | live | route to its class |
| endpoint `404`/`200` index | dead | record negative |
| secret authenticates/decodes | live | `web-auth-session` |
| secret fails/publishable | dead | record negative |
| flag endpoint public | a find | `web-logic-flaw` |
| flag endpoint `403` stays | server-enforced | record negative |
| flag shape passes `pre-flag` | the flag | submit |
| internal host unreachable | unverifiable | `web-ssrf` reach |

## The end-state decisions

| State | Action |
|---|---|
| every lead verified-or-dead | recon done — the exploit is the routed class |
| all leads dead + opaque strings | the route is dead — record + next layer |
| a flag candidate gated + live | the flag |
| a `.map`/lax signal | probe the adjacent surface |

## The bounded decision

When the pass ends — every lead verified-or-dead — the decision is the
routed class, not a second mining pass. A dead bundle does not re-mine.
