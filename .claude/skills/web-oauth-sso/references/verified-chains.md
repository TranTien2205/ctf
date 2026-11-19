# Verified chains — the OAuth/SSO chain cards that have been solved here

These are the verified chain cards — the OAuth/SSO shapes that have been
solved in this repository. A chain match is a candidate, not a proof —
verify the preconditions before running the card's probe.

## Card 1 — htb-ssos-oauth-registration-race-cookie-swap-json-csrf

**Challenge**: SSOS, HackTheBox, web.
**Stack**: Node.js, Express, EJS, passport-oauth2, Go, Gin, GORM, Nginx, Puppeteer.

### Preconditions

- SSO login ignores credential arguments and authorizes using whatever
  token cookie is in the shared browser jar.
- JSON-binding API parses raw JSON regardless of `Content-Type`.
- SSO token cookie is HttpOnly without `SameSite`.
- Registration endpoint allows pre-registration of a fixed account later
  used by the bot.

### Alternate preconditions

- A bot visiting user-supplied URLs with a shared cookie jar.
- A flag submitted once at bot startup.

### Signals

`oauth2`, `single sign on`, `jsessionid`, `connect.sid`, `registration race`,
`cookie swap`, `text/plain json csrf`, `shouldbindjson`, `puppeteer`,
`submit-url`, missing `samesite`, `loginSSO`, shared cookie jar.

### Chain

1. Win a registration race on the fixed bot account.
2. Use a `data:text/html` URL and `text/plain` cross-site JSON login to swap
   the bot's SSO token cookie.
3. Let the buggy `loginSSO` authorize using the swapped cookie.
4. Read the flag from the assignment submission as the now-owned account.

### First confirming probe

Hammer `POST /api/register` for the fixed bot account and confirm a
successful registration before the bot's startup registration step.

### Falsifier

The account is already registered with an unknown random password; the
instance is consumed.

### Known traps

- Registration race alone is insufficient — the CSRF uses `enctype=text/plain`
  and a JSON-name trick, not URL-encoded data.
- The bot's internal Nginx port differs from the external mapped port.
- `redirect_uri` validation is strict about hostname and port.
- Code exchange still requires the client secret — the cookie swap works
  because the bot performs the exchange.
- An already-started instance is permanently consumed.

## Card 2 — htb-apex-survive (crossed-token race → stored XSS → template-overwrite RCE)

This card is in `web-race-condition`, not `web-oauth-sso` — it anchors the
crossed-token race shape, not the OAuth flow. It is listed here because the
registration-race precondition (a fixed bot account, a shared cookie jar)
is the same shape.

## The card map

| Card | The entry shape | The chain | The sink |
|---|---|---|---|
| htb-ssos | registration race + cookie swap | register → swap → loginSSO → submit | `/submission/1` |
| htb-apex-survive | crossed-token race | race → XSS → template-overwrite | RCE |
