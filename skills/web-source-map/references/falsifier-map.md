# Falsifier map — every claim and its kill

## The route-existence falsifiers

| Claim | Kill |
|---|---|
| "there is a bundle" | entry page loads no app `.js` |
| "there is a map" | every `.map` probe 404/`text/html` |
| "the map has source" | `sourcesContent` null |
| "the bundle yields leads" | strings opaque, no endpoints/secrets |
| "the leads are real" | every lead's live check fails |

## The per-lead falsifiers

| Claim | Kill |
|---|---|
| endpoint real | 404 / a catch-all 200 serving the index |
| secret leaks | fails `Authorization`/decode / publishable |
| flag is a gate | server `403` regardless of the flag |
| route is server-side | `/api/x` 404s — a client path |
| map is a map | `200 text/html` — a catch-all |
| `sources` path is a file | it escapes `--out` — a traversal |
| recovered source is true | it is planted/dev-only |

## The anti-falsifier (reopen condition)

A falsifier has a precondition that reopens it:

- a `.map` 404 → reopens if the deployment ships a `.map` later or a
  dev bundle exists
- an endpoint 404 → reopens under a different host/prefix/session
- a secret dead → reopens if a different candidate verifies
- a flag server-enforced → reopens via a different gate mechanism

A falsifier is a *measurement* with a `reopen_if`, not a permanent
verdict.

## The kill-map usage

Each lead runs its falsifier — the live check is the falsifier. A lead
is real only while its falsifier has not fired; the route is dead only
when every lead's falsifier has fired. A fired falsifier is a recorded
negative, not a retry.

## The honest dead end

A mined bundle whose leads all fail is a clean depth-4 negative —
record it: `bundles_mined, leads_found, leads_dead, verdict:
negative`. The next solver does not re-walk it.
