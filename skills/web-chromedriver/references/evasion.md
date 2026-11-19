# Evasion — when the simple channel or read is blocked

## Exfil through a filtered outbound

When the bot's browser cannot reach your tunnel (egress filter,
interstitial, CSP), the exfil channel is the bug — not the payload:

| Blocked | Alternative channel |
|---|---|
| external `fetch` blocked by CSP `connect-src` | same-origin endpoint the app exposes (store the flag where you can read it), `navigate` to a same-origin path, a subresource CSP allows |
| all external requests blocked | a same-origin write the flag page renders; a stored value you read back |
| image/script allowed but not `fetch` | `new Image().src=...`, a `<script src>` — subresource CSP is often looser than `connect-src` |
| DNS only, no HTTP | a DNS exfil through a resolver you watch |
| an interstitial tunnel | a different tunnel without a confirm page; a raw TCP listener + port-forward |

The same-origin pivot is the reliable one: have the payload write the
flag into a same-origin location you can then read (a profile field, a
stored comment, an API you can query), rather than exfiltrating off-
origin.

## `file://` navigation blocked but JS allowed

When the endpoint refuses `file://` navigation but `execute` runs, try
`fetch("file:///...")` or an `XMLHttpRequest` inside the page — some
configs block the navigation scheme but not the JS file read. When
both are blocked, the file read is dead — pivot to reading the app's
own `localhost` HTTP routes instead.

## The navigation origin is sandboxed

Some drivers are configured to allow only the app's origin — `file://`
and external `http://` both refuse. Then the reachable set is the
app's own routes — read `localhost` admin/debug endpoints, and use the
browser's authenticated origin as the foothold rather than a file.

## A bot that hides its automation signals

If the challenge's anti-bot logic rejects `navigator.webdriver`, the
local reproduction must match — launch with
`--disable-blink-features=AutomationControlled` so the reproduction is
the same environment the payload actually faces. The point is a
faithful reproduction, not stealth for its own sake.

## CSP blocking the payload itself

When CSP blocks the payload's `eval`/`script`/`connect`, the fix is
the payload class (`../web-xss/` CSP bypasses) — but the channel
question stays here: which exfil the CSP's `connect-src`/`img-src`
still allows. Read the CSP header from the rendered page, not the
source you *think* the bot sees.

## Wait-time evasion

A bot with a fixed short wait kills a slow payload. Evade by making
the exfil synchronous: a `navigator.sendBeacon` (fire-and-forget,
survives navigation), an `Image` src (no await needed), or a same-
origin write that completes before the bot navigates away.

## The honest limit

Evasion here is about the *channel and the reproduction*, not about
hiding from the challenge's author. Do not chain an evasion to bypass
the challenge's own anti-cheat or a contest rule — the skill covers
reaching the flag through a real browser, not evading the rules of
the contest.
