# CSRF glossary — the terms the class uses

## A

- **ambient authority** — a credential the browser attaches
  automatically (cookie, IP position, shared jar) without the page
  asking; the thing CSRF rides.
- **anti-CSRF token** — a session-bound secret the form must echo;
  the distinguishing check.
- **ACAO/ACAC** — `Access-Control-Allow-Origin`/`-Allow-Credentials`;
  the CORS response headers that decide a cross-origin READ.

## B

- **bot** — a headless browser the challenge runs to visit a URL;
  the privileged viewer. also admin-bot, report-bot.
- **boundary (multipart)** — the delimiter between a multipart
  body's parts.

## C

- **confused deputy** — the server that can't tell a victim-intended
  request from an attacker-fired one.
- **cookie-plant** — writing a cookie into the victim's jar (a
  subdomain-set, a header-injection, a Set-Cookie response).
- **cross-site** — a different site (scheme+registrable-domain);
  what SameSite gates.
- **cross-origin** — a different origin (scheme+host+port); what
  CORS gates. broader than cross-site.
- **CSRF token** — see anti-CSRF token.

## D

- **delivery vehicle** — the browser/context that fires the request
  (a bot, a victim's browser, a stored page's viewer).
- **double-submit cookie** — a CSRF defense: a cookie + a form field
  must match; bypassed by controlling both.

## F

- **falsifier** — the condition that closes the class (a required
  unreadable token, a Strict cookie with no vector, an enforced
  Origin with no bypass).
- **family_leads** — a chain_match route: mechanism-vocabulary match,
  graded weak, a card to READ not a probe to run.
- **fetch metadata** — the `Sec-Fetch-*` headers the browser computes
  (Site/Mode/Dest/User).

## G

- **GET-write** — a state change reachable by a GET request; the
  Lax-open case.

## H

- **HttpOnly** — a cookie attribute: JS can't read it, but it still
  attaches to requests (doesn't stop CSRF attach).

## I

- **iframe-target** — a form's `target` naming an iframe — the
  response loads in the frame, the page stays.

## L

- **login-CSRF** — a CSRF that logs the victim into the attacker's
  account; the credential-plant write.
- **loopback write** — a write gated to 127.0.0.1/localhost; the
  bot's browser is the local client.

## N

- **no-cors** — a fetch mode that sends the request but makes the
  response opaque; the CSRF carrier.

## O

- **Origin** — the scheme+host+port of the page that issued the
  request; a browser-set header on cross-origin non-GET.
- **oracle** — the separate read that confirms a blind write landed.

## P

- **Partitioned** (CHIPS) — a cookie attribute: the cookie gets a
  per-top-site jar; kills third-party attach.
- **PNA** — Private Network Access: a public-context page can't
  fetch a private address without a preflight; a form nav isn't
  PNA-gated.
- **preflight** — the OPTIONS request a non-simple CORS request
  triggers; fails without CORS-open.

## R

- **readback** — reading the state the write changed, by a separate
  request; the CSRF confirmation.
- **Referer** — the full URL of the page that issued the request;
  suppressible via no-referrer, not spoofable via JS.
- **remote_ip** — the socket peer; a localhost gate that reads it
  can't be header-spoofed — only a local client passes.

## S

- **same-site** — same registrable domain (incl. subdomains);
  different from same-origin.
- **SameSite** — the cookie attribute: Strict/Lax/None decides
  cross-site attach.
- **Sec-Fetch-Site** — fetch metadata: same-origin|same-site|cross-
  site|none.
- **state change** — a write (POST/PUT/DELETE, or a GET-with-side-
  effect); what CSRF fires.
- **stored-CSRF** — a CSRF page stored on the target's own origin;
  same-origin, bypasses cross-site gates.
- **sub-resource** — a request a page embeds (img/script/fetch) —
  not a top-nav; Lax blocks it.

## T

- **text/plain** — the form content-type that ships a body unencoded;
  the JSON carrier.
- **token-binding** — whether the CSRF token is tied to the session;
  the bypass question.
- **top-level navigation** — the main-frame document load; the Lax
  exception applies to GET navs.

## W

- **ws-hijack** — a cross-site WebSocket channel; the handshake
  carries cookies.
