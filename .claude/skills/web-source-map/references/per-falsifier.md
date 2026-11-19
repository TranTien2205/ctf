# Per-falsifier — one kill per claim

| The claim | The falsifier | On falsify |
|---|---|---|
| "a bundle exists" | entry page loads no `.js` app code | not this route |
| "the map is reachable" | `.map` 404s everywhere / `200 text/html` catch-all | string mine |
| "the map has source" | `sources` present, `sourcesContent` null | file names only |
| "the endpoint is real" | the string 404s live | dead client route — record |
| "the secret is a leak" | it does not authenticate/decode | record negative |
| "the flag is a gate" | server enforces the flag | dead — record |
| "the route is server-side" | a 404 — pure client path | record |
| "recovered the source" | only strings grepped, no map | a grep, not source |
| "the source is trustworthy" | a `sources` traversal rejected | attacker-planted |
| "this is the vuln" | all leads public/dead/unexploitable | recon done, no bug |
| "re-mining helps" | a dead bundle's strings are fixed | next layer |

## The honest posture

Every lead the map produces carries its falsifier — the live check.
A lead is real only while its falsifier has not fired. The route is
dead only when every lead's falsifier has fired.

## The anti-pattern

Presenting a mined string as a finding without running its falsifier —
"the bundle has `/api/admin`" is not "the server exposes `/api/admin`".
The falsifier *is* the finding.
