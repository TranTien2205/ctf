# Decision table — every state and its next action

## The discovery decisions

| State | Action |
|---|---|
| a `check-username`/`available` endpoint exists | direct oracle — confirm in one request |
| register returns `"taken"`/`409` | register oracle — confirmed |
| a `?error=`/`?e=` on the login redirect | redirect oracle — `Location` diff |
| both arms `200` identical body | check status/side, then timing |
| a `Set-Cookie`/header/JSON-field differs | side oracle — envelope diff |
| `good` measurably slower | timing oracle — N>=8 median |
| a `423`/`429` on a real name | lock oracle + throttle — measure N |
| every channel uniform on a form | that form closed — next form |

## The measurement decisions

| State | Action |
|---|---|
| `bad1`!=`bad2` in per-request fields | mask the noise, then diff |
| a one-off anomaly | re-send exact — no-repeat = closed |
| sub-jitter timing | weak hash — content channel or record sub-jitter |
| a `403`/`CSRF` on both arms | re-fetch token per request — unpaired |
| a cached response | cache-bust param — unmeasured until busted |
| load-balanced timing | pin a session cookie for affinity |

## The throttle decisions

| State | Action |
|---|---|
| no `429`/`423`/delay in 15 | throttle absent — record the count |
| `429`/`423` at N | threshold — record N, probe bypass |
| `X-Forwarded-For` resets `429` | bypassed — the finding, record it |
| a CAPTCHA after N | throttle + the content oracle may fire pre-N |
| a per-second window | the window is the limit — a slow spray passes |

## The route decisions

| Confirmed | Route |
|---|---|
| a verified account name | `web-auth-session`/`web-idor`/`web-logic-flaw`/`web-oauth-sso` |
| `admin`/`service`/`backup` | weak/default password → `web-auth-session` |
| a `/api/users/{name}` 200 | `web-idor` |
| a reset that reveals + a reset-bug | `web-auth-session`/`web-logic-flaw` |
| an email-collision | `web-oauth-sso` |
| a no-throttle/bypass | `web-auth-session` credential loop |

## The end-state decisions

| State | Action |
|---|---|
| every form measured oracle-or-uniform | enum done — route or negative |
| a confirmed name + a chain to it | hand to the neighbor class |
| all-uniform everywhere | record negative — the chain moves |
