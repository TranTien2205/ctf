# Class boundary (deep) — the exact handoff contract

## This layer's job

`web-source-map` is a **recon layer** — it produces verified leads. It
does not exploit them. The boundary: `mine → name → verify → route`,
then stop; the routed class does `exploit → find → flag`.

## vs `web-triage`

`web-triage` decides *which class* a challenge is from observed
signals. `web-source-map` *feeds* triage — the map surfaces the
endpoints and params triage then classifies. Run the map early when a
SPA ships; it names the surface triage would otherwise guess at. The
map is upstream of triage.

## vs `file-read-primitives`

Both expose "source". `file-read-primitives` reads *server-side* files
through a traversal/LFI — the backend source. `web-source-map` recovers
*client-side* source the server *shipped* — a `.map` is not an LFI; it
is a file the server serves publicly. A `.map` recovery is a public
read; a `.git`/`/src/` traversal is `file-read-primitives`.

## vs `web-info-disclosure`

Adjacent — a `.map` file is often the info-disclosure vector. The
distinction: `web-info-disclosure` is the *bug* (the server should not
ship the map/key/.git), `web-source-map` is the *technique* (how to
mine what shipped). The map is the mechanism; the disclosure is the
class.

## vs `web-info-disclosure` for secrets

A secret in the bundle is the *technique's* find; whether it is a *bug*
is `web-info-disclosure`'s verdict (a publishable `pk_` is not a leak; a
private `sk_` is). The map produces the candidate; the disclosure class
judges it.

## vs `web-xss` (the DOM sink)

A recovered-source `innerHTML`/`dangerouslySetInnerHTML`/`eval` is a
*client-side* sink — a DOM-XSS surface, `web-xss`. The map's source
shows the sink; `web-xss` exploits it.

## The handoff contract

Every lead carries:

```
lead = {
  string: <the verbatim mined string>,
  source_file: <which bundle/map it came from>,
  verify_result: <live / dead / unverifiable>,
  route: <the class it feeds>
}
```

A lead without its `source_file` and `verify_result` is not traceable.
The routed class takes it from there.

## The recon-not-bug reminder

The map's job is to make the surface *enumerable* — it turns the hidden
client-side surface into a verified lead list. The bug is what the
routed class finds *in* that surface.
