# CSRF - cross-site request forgery

**When:** a state-changing endpoint relies on ambient authority (cookies,
basic auth, client certs) with no anti-CSRF token or SameSite protection.

## Audit a state-changing request

Record the real request (from crawl forms or your session), then check:

1. Is there a CSRF token? In body, header (`X-CSRF-Token`, `X-XSRF-TOKEN`),
   or double-submit cookie? Missing = likely vulnerable.
2. Remove/blank the token -> does the request still succeed? Token presence
   without validation is the same as absent.
3. Token from another session/account accepted? -> not bound to user.
4. Cookie `SameSite`: `Lax`/`Strict` blocks most CSRF POSTs; `None` needs
   Secure + usually an OAuth intent; absent defaults vary by browser.
5. Content-Type bypass: endpoint accepts `text/plain`/form-encoded while
   the SPA sends JSON -> a plain HTML form can forge the write.

## GET endpoints

State changes on GET are CSRF by default (img tag = request). Record any
GET that mutates state as its own finding. `probe_csrf` flags GET forms
whose action looks state-changing (update/delete/set/...) as leads -
confirm the endpoint really mutates state before recording.

## Minimal PoC for a report

A static HTML form that replays the request cross-origin, plus the recorded
successful response. You do not need to execute it in a real browser to
rate it - the missing check on a working authenticated write is the bug.

## What does NOT count

- Login/logout forms alone: low-impact CSRF, mention briefly
- Endpoints requiring a custom header the form can't set (that header IS
  the CSRF defense when combined with CORS policy) - verify CORS first
- JSON-only APIs with enforced Content-Type and sane CORS

## Severity guide

CSRF on password/email change or privileged action: medium-high. On
low-impact preference: low. Missing SameSite on session cookie alone: info.
