# Case studies — the shapes bundle recon takes

## Catalogue note

No `web-source-map`-led challenge is solved in this repository yet —
these are standard published shapes, not local verified chains. Record
a real solve into `../field-notes.md` to promote the class.

## The hidden admin route

A React SPA shows a login page. `main.js` + the route table in a chunk
names `/admin`, `/internal/api`, `/dashboard/secret` — routes the UI
hides behind auth. The map (or a string grep) surfaces the route table;
the routes are client-side paths but a few map to real server
endpoints. Probing `/internal/api` returns data the UI never showed —
the map handed an IDOR/logic target the rendered page hid.

## The leaked key

A `config.js` chunk carries `apiKey: "sk_live_..."`, a
`REACT_APP_SECRET`, or a JWT in `localStorage.setItem`. `bundle_miner
--show-secrets` surfaces the candidate; the live check authenticates.
The key unlocks an endpoint the UI gated — a real credential left in
client source. Routes to `web-auth-session`.

## The feature flag

The bundle gates a feature behind `feature.beta` / `config.debug` /
`flags.internal` — the UI checks the flag, the server does not. The
map names the flag and the endpoint it gates; setting the flag (a
request param, a localStorage key, a header the client sends) reaches
the gated behavior. Routes to `web-logic-flaw` / `web-mass-assignment`.

## The internal URL

The bundle builds a fetch to `http://internal.svc/` or
`https://api.internal.example.com` — an internal host the client calls
server-side or that an SSRF surface can reach. The map names the
internal target; an SSRF probe reaches what the browser cannot. Routes
to `web-ssrf`.

## The flag in a comment

The challenge flag is literally in a recovered source — a `// flag{...}`
comment, a `const FLAG`, an env var the build inlined. `bundle_miner`
surfaces it; `pre-flag` gates it before submission. A common CTF shape.

## The `.git`-adjacent map

A `.map` request returns the map, and a `/.git/HEAD` or `/.env` probe
on the same host returns more — the deployment left everything public.
The map is one vector among several info-disclosure paths; the mining
order is map → `.git` → `.env` → backups.

## The Next.js route leak

`/_next/static/[buildId]/_buildManifest.js` lists every page route —
`/admin`, `/api/internal`, `/debug` — including ones no link reaches.
The manifest is a route map the UI does not show; each named route is a
probe target.
