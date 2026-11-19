# Per-boundary — where this recon layer ends

## The recon/exploit boundary

`web-source-map` ends where the exploit begins. It produces verified
leads; the routed class exploits them. The boundary is:

- **this layer**: `mine → name → verify → route` — produce the lead
- **next layer**: the routed class — `web-idor`/`web-auth-session`/etc. —
  work the lead into a finding

Do not drift into the exploit while in the recon pass — route it.

## The front-end/back-end boundary

The map is the *front-end* source — the client logic shipped to the
browser. The server logic is only what the client shipped as a hint —
an endpoint call, a param name, a `fetch` URL. A recovered source shows
the *client's view* of the server, not the server's source. Server
source is a different artifact (`.git`, `.env`, `file-read`).

## The map/string boundary

- `.map` + `sourcesContent` → the *original commented source*
- no map → *string literals only* (endpoints, params, secrets survive;
  the logic does not)

Do not claim the source when you have the strings.

## The lead/finding boundary

A bundle string is a *lead* (surface/claim), not a *finding*
(class/impact). It becomes a finding only when its live check passes
AND the routed class exploits it. The recon layer produces leads; the
finding is downstream.

## The client/server gate boundary

A client-side gate (`PrivateRoute`, `meta.requiresAuth`, `feature.X`)
is a *client* check — bypassable if the server does not re-check. The
boundary: the client's gate is a lead; the server's enforcement is the
falsifier.

## The catalogue/verified boundary

This class is **catalogue** — no local verified solve. The shapes are
standard published knowledge; do not present them as "what worked
here". A real map-led solve in `../field-notes.md` promotes it.

## The trust boundary

The bundle/map are attacker-controlled — read recovered source, never
execute it; a `sources` traversal is rejected, not recovered; a
"secret" is a candidate until it verifies live.
