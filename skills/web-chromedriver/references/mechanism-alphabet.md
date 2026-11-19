# Mechanism alphabet — the primitives, A–Z

## A — Async execute (`execute/async`)

The JS primitive for promises: blocks until `arguments[last]` is
invoked. Use for `fetch` chains so the resolved value returns, not a
pending promise. Bounded by `timeouts.script`.

## B — Back/Forward/Refresh

The history commands — rare primitives, but the mechanism for
navigating a multi-step flow the bot follows through history.

## C — Capabilities

The session-create JSON — `alwaysMatch`/`firstMatch`, `browserName`,
`browserVersion`, `platformName`, `goog:chromeOptions`. Picks the
browser and its flags; a mismatch returns `No matching capabilities`.

## D — DELETE /session

The mandatory cleanup — releases the browser process. A leaked session
is a leaked browser; on a shared endpoint, a held slot.

## E — Execute (`execute/sync`)

`Runtime.evaluate` in the page — the richest read. Origin + cookies
inherited; JSON-safe return only (elements -> refs, `undefined` ->
null, promises -> pending unless async).

## F — File read (`file://` nav)

Navigate to `file:///path` + `source` — the file's text wrapped in
`<html><pre>`. The primary read on an exposed endpoint. The `execute`
`fetch("file://")` form is a separate primitive when nav is blocked.

## G — Grid

Selenium's hub on `:4444` — routes sessions to nodes by capability.
`GET /status` names the node inventory (browsers/versions/platforms);
the reads land on the *node's* filesystem/network.

## H — HttpOnly jar read (`GET /cookies`)

The cookie jar — `HttpOnly` restricts `document.cookie`, not the jar.
The read that surfaces a flag cookie JS cannot see.

## I — Insecure certs (`acceptInsecureCerts`)

The capability for self-signed/bad certs — a `true` here avoids the
`ERR_SSL` on a challenge's self-signed endpoint.

## J — JSON wire protocol

The serialisation between driver and client — JSON-safe values only.
Explains why `return el` gives a reference and `return el.outerHTML`
gives the text.

## K — Kill map

The measured dead-end record — endpoint/file/js/loopback/reproduction/
channel/flag/bot cells, each with a re-open condition.

## L — Loopback reach (`localhost` nav)

The browser's host position — `localhost` is the app's loopback;
internal routes the external view cannot reach. A positional surface.

## M — Match (the reproduction)

The reproduction-fidelity property: transfers iff URL/cookie/wait/
flags/version match live. A divergence = a different bot.

## N — Network hooks

`page.on("request"/"requestfailed")` / CDP `Network.*` — the exfil
and the block observer. `requestfailed` catches what never got a
response (CSP/DNS/TLS).

## O — Origin (same-origin reach)

`execute` inherits the browser's origin + cookies — same-origin APIs,
`localStorage`, the flag page the origin can fetch.

## P — Page source (`GET /source`)

The rendered DOM — a `file://` read, a page's live tree. The default
read-back after any navigation.

## Q — Query (the element find)

`POST /element` `{"using","value"}` -> an opaque handle; goes stale on
DOM mutation — `stale element reference`.

## R — Reproduction

The local bot matching the challenge's bot — the debugging aid's core.
Built from the bot's spec; the fidelity property governs its transfer.

## S — Screenshot (`GET /screenshot`)

The rasterised viewport — a flag-as-image or a mangled-text flag. The
PNG is the artifact.

## T — Timeouts

`timeouts` `{script,pageLoad,implicit}` — per-command bounds. A hang
bounded, not a stall.

## U — URL navigate (`POST /url`)

The navigation command — `file://`, `http://`, `localhost`, external —
the browser's normal loader.

## V — Version match

`chromedriver` must match the browser's major version — a mismatch
fails at session create, before any command.

## W — WebDriver

The W3C HTTP+JSON protocol — the portable command set every client
library wraps.

## X — eXfil

The outbound request carrying the flag — `fetch`/`Image`/`sendBeacon`/
`script`/form/`top.location` — or the same-origin write-back.

## Y — (w)ait

The bot's wait — the payload's execution budget. `wait_for_timeout`,
`wait_for_selector`, `networkidle` — match its shape.

## Z — Zone (the frame)

`POST /frame` — the current-frame boundary `execute`/`source` operate
on; the driver crosses what JS cannot.

## The alphabet-to-file map

| Letter | Depth in |
|---|---|
| A,E,J | `mechanism-deep.md`, `per-mechanism-deep.md` |
| C,V | `capabilities.md`, `chrome-flags.md` |
| F,H,L,O | `attack-surface-deep.md`, `per-surface-deep.md` |
| G | `grid-remote.md` |
| K | `falsifier-map.md`, `negative-results.md` |
| M,R | `local-bot.md`, `local-bot-deep.md` |
| N | `observability.md`, `cdp.md` |
| P,S | `mechanism.md` |
| Q,Z | `multi-page.md` |
| T | `session-management.md` |
| U | `webdriver-api.md`, `per-endpoint.md` |
| W | `webdriver-api.md` |
| X | `payload-variants.md`, `payload-variants-deep.md` |
| Y | `local-bot.md`, `payload-development.md` |
