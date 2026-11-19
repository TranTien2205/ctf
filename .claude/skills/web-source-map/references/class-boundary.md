# Class boundary — what source-map recon is, and what it feeds

## The boundary

`web-source-map` is a **recon layer, not a bug class**. It mines the
front-end for leads and hands them to the class that owns them:

| The map produced | Route to |
|---|---|
| an endpoint taking an object id | `../web-idor/` |
| an endpoint with a query body | `../web-sqli/` / `../web-nosqli/` |
| a template-rendered param | `../web-ssti/` |
| a server-side fetch URL | `../web-ssrf/` |
| a file/download path | `../file-read-primitives/` |
| a verified key/token | `../web-auth-session/` |
| a hidden admin route / feature flag | `../web-logic-flaw/` / `../web-mass-assignment/` |
| an internal host | `../web-ssrf/` |
| a flag-shaped string | `pre-flag` → the challenge's flag path |
| a deserialization-looking param | `../web-deserialization/` |
| a GraphQL endpoint | `../web-graphql/` |

## What it is NOT

- **not directory brute force** — the bundle *names* real endpoints;
  `web-triage`/ffuf guess paths, the map enumerates them
- **not a vulnerability** — it produces the input to one
- **not backend source** — the map is the *front-end* source; server
  logic is only what shipped to the client
- **not deobfuscation** — a minified bundle with no map yields strings,
  not the real program; do not claim to have "read the source" when
  you grepped strings

## vs `web-triage`

`web-triage` decides *which class* a challenge is from observed
signals. `web-source-map` *feeds* triage — the map surfaces the
endpoints and params triage then classifies. Run the map early when a
SPA ships; it names the surface triage would otherwise guess at.

## vs `file-read-primitives`

Both expose "source". `file-read-primitives` reads *server-side* files
through a traversal/LFI — the backend source. `web-source-map` recovers
*client-side* source the server *shipped* — a different artifact. A
`.map` is not an LFI; it is a file the server serves publicly.

## vs `web-info-disclosure`

Adjacent — a `.map` file is often the info-disclosure vector. The
distinction: `web-info-disclosure` is the *bug* (the server should not
ship the map/key), `web-source-map` is the *technique* (how to mine
what shipped). The map is the mechanism; the disclosure is the class.

## The handoff contract

Every lead the map produces carries: the source file it came from, the
verbatim string, and the follow-on class. Record the lead in state so
the next layer knows where it came from — "endpoint `/api/admin` from
`main.js`" is traceable; "found an endpoint" is not.
