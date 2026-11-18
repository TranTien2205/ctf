# Browser behavior matrix — the engine differences that decide CSRF

SameSite defaults, PNA handling, ws-cookie behavior, and the legacy
edge cases differ across Chrome/Firefox/Safari and their versions.
The bot's engine decides which rules actually apply.

---

## 1. The SameSite-default matrix — missing attribute

| Engine | Version | Missing-SameSite default |
|---|---|---|
| Chrome/Edge | ≥80 | Lax |
| Chrome/Edge | ≤79 | None-equivalent |
| Firefox | ≥96 | Lax (rolled out later) |
| Firefox | <96 | None-equivalent |
| Safari | all | None-equivalent (no Lax-by-default) |
| a headless bot's chromium | varies | the launch flag decides |

The bot's chromium version matters — a bot on an older build or
with `--disable-features=SameSiteByDefaultCookies` attaches like
None.

## 2. The `Lax+POST` grace window — the historical edge

```text
Chrome ~80-85 shipped a 'Lax+POST' exception: a freshly-set cookie
(without an explicit SameSite) attached to cross-site POSTs for 2
minutes after being set — to not break SSO flows. dead on modern
builds; a history note for an old-bot challenge.
```

## 3. The PNA matrix — private-network rules

| Engine | PNA behavior |
|---|---|
| Chrome ≥94 | private-network preflight on fetch/xhr to RFC1918/loopback from public contexts |
| Chrome | `--disable-features=BlockInsecurePrivateNetworkRequests` turns it off |
| Firefox | PNA not enforced the same way |
| Safari | weaker PNA |
| a form top-nav to loopback | NOT PNA-gated the same as fetch in any engine |

## 4. The ws-handshake cookie matrix

| Engine | ws cookie under SameSite |
|---|---|
| older Chrome/Firefox | attaches regardless of SameSite (ws wasn't gated) |
| newer Chrome | Lax blocks ws cross-site like other sub-requests |
| a bot's chromium | the build decides — test or grep the version |

## 5. The Origin-on-GET matrix

| Engine | Origin header on cross-origin GET |
|---|---|
| Chrome | usually sends Origin on fetch, omits on top-nav GET |
| Firefox | may omit Origin on same-origin GET |
| a form GET | Origin often absent — a GET nav has no Origin |

## 6. The Referer-suppression matrix

```text
- <meta name=referrer content=no-referrer> — works in all engines
- Referrer-Policy: no-referrer — all engines
- a data:/about:/javascript: origin — no Referer in all engines
- a top-nav that goes through a referrer-stripping hop — the Referer
  reflects the LAST page, or none
```

## 7. The sendBeacon/keepalive matrix

```text
sendBeacon fires even on page-unload — reliable across engines.
fetch keepalive:true — a fetch that survives unload — newer engines.
a bot that closes the page fast — sendBeacon is the reliable carrier.
```

## 8. The cookie-attach-on-Set matrix — a cross-origin Set-Cookie

```text
a cross-origin response's Set-Cookie is STORED by the browser per
the cookie's own attributes — a SameSite=Lax cookie set via a cross-
site response: Chrome blocks third-party SET of Lax cookies (a
cross-site response can't set a Lax cookie) but a missing-SameSite
or a None cookie sets. the SSOS card's swap needed the cookie to
set cross-site — a missing-SameSite token cookie.
```

| Cookie | Cross-site Set lands? |
|---|---|
| SameSite=Strict | blocked (third-party set) |
| SameSite=Lax | blocked on modern |
| SameSite=None+Secure | lands |
| missing | engine-dependent — older lands |

## 9. The iframe/third-party-cookie matrix

```text
a third-party iframe's cookies:
- Chrome: third-party cookies blocked by default (ITP-equivalent
  shipping); a Partitioned cookie gets its own jar
- Firefox: Total Cookie Protection — third-party cookies partitioned
- Safari: ITP — third-party cookies blocked aggressively
an iframe-embedded CSRF page can't use the victim's cookies under
modern third-party blocking — a top-nav or a Partitioned-aware path
```

## 10. The engine-detection — which browser is the bot

```bash
# the bot's UA / launch config from source
grep -rnoE 'puppeteer|playwright|headless|chromium|chrome|firefox|webkit|userAgent|User-Agent|args' <src> | head -20
# a puppeteer default is bundled-chromium (recent); playwright lets
# you pick; selenium+chromedriver is the host's chrome version
```

## 11. The matrix→decision

```text
the bot's engine decides which SameSite/PNA/ws rules apply:
- an old-chromium bot → missing-SameSite=None → full CSRF surface
- a modern bot → missing-SameSite=Lax → GET-nav only
- a PNA-enforcing bot → fetch-to-loopback blocked → form nav
- a third-party-blocked bot → iframe CSRF can't use cookies → top-nav
```

## 12. The falsifier

```text
a modern-engine bot + a Partitioned/Strict cookie + PNA-enforced —
the CSRF surface closes on this engine. the falsifier is engine-
specific — a different viewer (a stored page's real-user view) may
still be open.
```
